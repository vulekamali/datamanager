import logging
import re
import uuid
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal
from pprint import pformat
from urllib.parse import quote

import requests
from slugify import slugify

from adminsortable.models import SortableMixin
from autoslug import AutoSlugField
from budgetportal.datasets import Dataset, get_expenditure_time_series_dataset
from ckeditor.fields import RichTextField
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.cache import cache
from django.db import models
from django.urls import reverse
from partial_index import PartialIndex

logger = logging.getLogger(__name__)
ckan = settings.CKAN

URL_LENGTH_LIMIT = 2000

CKAN_DATASTORE_URL = settings.CKAN_URL + "/api/3/action" "/datastore_search_sql"

MAPIT_POINT_API_URL = "https://mapit.code4sa.org/point/4326/{},{}"

DIRECT_CHARGE_NRF = "Direct charge against the National Revenue Fund"

prov_abbrev = {
    "Eastern Cape": "EC",
    "Free State": "FS",
    "Gauteng": "GT",
    "KwaZulu-Natal": "NL",
    "Limpopo": "LP",
    "Mpumalanga": "MP",
    "Northern Cape": "NC",
    "North West": "NW",
    "Western Cape": "WC",
}

# Budget Phase IDs for the 7-year overview period
TRENDS_AND_ESTIMATES_PHASES = [
    "Audited Outcome",
    "Audited Outcome",
    "Audited Outcome",
    "Adjusted appropriation",
    "Main appropriation",
    "Medium Term Estimates",
    "Medium Term Estimates",
]

EXPENDITURE_TIME_SERIES_PHASES = (
    "Main appropriation",
    "Adjusted appropriation",
    "Final Appropriation",
    "Audit Outcome",
)

EXPENDITURE_TIME_SERIES_PHASE_MAPPING = {
    "original": "Main appropriation",
    "adjusted": "Adjusted appropriation",
    "actual": "Audit Outcome",
}


class Homepage(models.Model):
    main_heading = models.CharField(max_length=1000, blank=True)
    sub_heading = models.CharField(max_length=1000, blank=True)
    primary_button_label = models.CharField(max_length=1000, blank=True)
    primary_button_url = models.CharField(max_length=1000, blank=True)
    primary_button_target = models.CharField(max_length=1000, blank=True)
    secondary_button_label = models.CharField(max_length=1000, blank=True)
    secondary_button_url = models.CharField(max_length=1000, blank=True)
    secondary_button_target = models.CharField(max_length=1000, blank=True)
    call_to_action_sub_heading = models.CharField(max_length=1000, blank=True)
    call_to_action_heading = models.CharField(max_length=1000, blank=True)
    call_to_action_link_label = models.CharField(max_length=1000, blank=True)
    call_to_action_link_url = models.CharField(max_length=1000, blank=True)
    call_to_action_link_target = models.CharField(max_length=1000, blank=True)


class FinancialYear(models.Model):
    organisational_unit = "financial_year"
    slug = models.SlugField(max_length=7, unique=True)
    published = models.BooleanField(default=False)
    _consolidated_expenditure_budget_dataset = None

    class Meta:
        ordering = ["-slug"]

    @property
    def national(self):
        return self.spheres.filter(slug="national")[0]

    @property
    def provincial(self):
        return self.spheres.filter(slug="provincial")[0]

    def get_url_path(self):
        return "/%s" % self.slug

    def get_starting_year(self):
        return self.slug[:4]

    @staticmethod
    def slug_from_year_start(year):
        return year + "-" + str(int(year[2:]) + 1)

    @staticmethod
    def start_from_year_slug(slug):
        return slug[:4]

    def get_sphere(self, name):
        return getattr(self, name)

    def get_closest_match(self, department):
        sphere = self.spheres.filter(slug=department.government.sphere.slug).first()
        government = sphere.governments.filter(slug=department.government.slug).first()
        department = government.departments.filter(slug=department.slug).first()
        if not department:
            return government, False
        return department, True

    @classmethod
    def get_available_years(cls):
        years = list(cls.objects.filter(published=True).order_by("-slug")[:4])
        years.reverse()
        return years

    @classmethod
    def get_latest_year(cls):
        return cls.objects.filter(published=True).order_by("-slug")[0]

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, self.get_url_path())


class Sphere(models.Model):
    organisational_unit = "sphere"
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from="name", max_length=200, always_update=True)
    financial_year = models.ForeignKey(
        FinancialYear, on_delete=models.CASCADE, related_name="spheres"
    )

    class Meta:
        unique_together = (("financial_year", "slug"), ("financial_year", "name"))
        ordering = ["-financial_year__slug", "name"]

    def get_url_path(self):
        return "%s/%s" % (self.financial_year.get_url_path(), self.slug)

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, self.get_url_path())


class Government(models.Model):
    organisational_unit = "government"
    sphere = models.ForeignKey(
        Sphere, on_delete=models.CASCADE, related_name="governments"
    )
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from="name", max_length=200, always_update=True)
    _function_budgets = None

    class Meta:
        unique_together = (("sphere", "slug"), ("sphere", "name"))

    def get_url_path(self):
        if self.sphere.slug == "national":
            return self.sphere.get_url_path()
        else:
            return "%s/%s" % (self.sphere.get_url_path(), self.slug)

    def get_department_by_slug(self, slug):
        departments = self.departments.objects.filter(slug=slug)
        if departments.count() == 0:
            return None
        elif departments.count() == 1:
            return departments.first()
        else:
            raise Exception("More matching slugs than expected")

    def get_vote_primary_departments(self):
        return Department.objects.filter(government=self, is_vote_primary=True).all()

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, self.get_url_path())


class Department(models.Model):
    organisational_unit = "department"
    government = models.ForeignKey(
        Government, on_delete=models.CASCADE, related_name="departments"
    )
    name = models.CharField(
        max_length=200,
        help_text="The department name must precisely match the text used in the Appropriation "
        "Bill. All datasets must be normalised to match this name. Beware that changing "
        "this name might cause a mismatch with already-published datasets which might "
        "need to be update to match this.",
    )
    slug = AutoSlugField(
        populate_from="name", max_length=200, always_update=True, editable=True
    )
    vote_number = models.IntegerField()
    is_vote_primary = models.BooleanField(default=True)
    intro = models.TextField()
    website_url = models.URLField(default=None, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        self._programme_budgets = None
        self._econ_by_programme_budgets = None
        self._prog_by_econ_budgets = None
        self._adjusted_estimates_of_expenditure_dataset = None
        self._estimates_of_econ_classes_expenditure_dataset = {}
        self._estimates_of_subprogramme_expenditure_dataset = None
        self._expenditure_time_series_dataset = None
        super(Department, self).__init__(*args, **kwargs)

    class Meta:
        unique_together = (("government", "slug"), ("government", "name"))
        indexes = [
            PartialIndex(
                fields=["government", "vote_number"],
                unique=True,
                where="is_vote_primary",
            )
        ]

        ordering = ["vote_number", "name"]

    def clean(self):
        # This is only for user feedback in admin.
        # The constraint must be enforced elsewhere.
        existing_vote_primary = Department.objects.filter(
            government=self.government, vote_number=self.vote_number
        )
        if (
            self.is_vote_primary
            and existing_vote_primary
            and existing_vote_primary.first() != self
        ):
            raise ValidationError(
                "There is already a primary department for "
                "vote %d" % self.vote_number
            )

    @classmethod
    def get_in_latest_government(cls, name, government_name):
        """
        Get a department instance whose slug matches the provided name slugified,
        in the government with the provided name in the latest financial year.
        Returns None if a matching department is not found.
        """
        try:
            return cls.objects.filter(
                slug=slugify(name), government__name=government_name
            ).order_by("-government__sphere__financial_year__slug")[0]
        except IndexError:
            return None

    def create_dataset(self, name, title, group_name):
        vocab_map = get_vocab_map()
        tags = [
            {
                "vocabulary_id": vocab_map["spheres"],
                "name": self.government.sphere.slug,
            },
            {
                "vocabulary_id": vocab_map["financial_years"],
                "name": self.get_financial_year().slug,
            },
        ]
        if self.government.sphere.slug == "provincial":
            tags.append(
                {"vocabulary_id": vocab_map["provinces"], "name": self.government.name}
            )
        dataset_fields = {
            "title": title,
            "name": name,
            "groups": [{"name": group_name}],
            "extras": [
                {"key": "department_name", "value": self.name},
                {"key": "Department Name", "value": self.name},
                {"key": "department_name_slug", "value": self.slug},
                {"key": "Vote Number", "value": self.vote_number},
                {"key": "vote_number", "value": self.vote_number},
                {"key": "geographic_region_slug", "value": self.government.slug},
                {"key": "organisational_unit", "value": "department"},
            ],
            "owner_org": "national-treasury",
            "license_id": "other-pd",
            "tags": tags,
        }
        logger.info("Creating package with %r", dataset_fields)
        return Dataset.from_package(ckan.action.package_create(**dataset_fields))

    def get_latest_website_url(self):
        """ Always return the latest available non-null URL, even for old departments. """
        newer_departments = Department.objects.filter(
            government__slug=self.government.slug,
            government__sphere__slug=self.government.sphere.slug,
            slug=self.slug,
            website_url__isnull=False,
        ).order_by("-government__sphere__financial_year__slug")
        return newer_departments.first().website_url if newer_departments else None

    def get_url_path(self):
        """ e.g. 2018-19/national/departments/military-veterans """
        return "%s/departments/%s" % (self.government.get_url_path(), self.slug)

    def get_preview_url_path(self):
        """ e.g. 2018-19/previews/national/south-africa/agriculture-and-fisheries """
        return "%s/previews/%s/%s/%s" % (
            self.government.sphere.financial_year.slug,
            self.government.sphere.slug,
            self.government.slug,
            self.slug,
        )

    def get_govt_functions(self):
        return GovtFunction.objects.filter(programme__department=self).distinct()

    def get_financial_year(self):
        return self.government.sphere.financial_year

    def get_latest_department_instance(self):
        """ Try to find the department in the most recent year with the same slug.
        Continue traversing backwards in time until found, or until the original year has been reached. """
        newer_departments = Department.objects.filter(
            government__slug=self.government.slug,
            government__sphere__slug=self.government.sphere.slug,
            slug=self.slug,
        ).order_by("-government__sphere__financial_year__slug")
        return newer_departments.first() if newer_departments else None

    def _get_financial_year_query(self):
        return '+vocab_financial_years:"%s"' % self.get_financial_year().slug

    def _get_government_query(self):
        if self.government.sphere.slug == "provincial":
            return '+vocab_provinces:"%s"' % self.government.name
        else:
            return none_selected_query("vocab_provinces")

    def get_primary_department(self):
        """
        Check if department is primary
        """
        if not self.is_vote_primary:
            try:
                dept = Department.objects.get(
                    vote_number=self.vote_number,
                    is_vote_primary=True,
                    government=self.government,
                )
            except MultipleObjectsReturned:
                logger.exception(
                    "Department %s has multiple primary " "departments" % self.slug
                )
                raise
            else:
                return dept
        return self

    def get_dataset(self, group_name, name=None):
        """
        Get a dataset correctly annotated to match this department.
        If name isn't provided, still assume there's just one dataset
        in the specified group categorised to match this department.
        """
        query = {
            "q": "",
            "fq": (
                '+organization:"national-treasury"'
                '+vocab_financial_years:"%s"'
                '+vocab_spheres:"%s"'
                '+extras_s_geographic_region_slug:"%s"'
                '+extras_s_department_name_slug:"%s"'
                '+groups:"%s"'
            )
            % (
                self.government.sphere.financial_year.slug,
                self.government.sphere.slug,
                self.government.slug,
                self.get_primary_department().slug,
                group_name,
            ),
            "rows": 1,
        }
        if name:
            query["fq"] += '+name:"%s"' % name
        response = ckan.action.package_search(**query)
        logger.info(
            "query %s\nreturned %d results", pformat(query), len(response["results"])
        )
        if response["results"]:
            assert len(response["results"]) == 1
            return Dataset.from_package(response["results"][0])

    def _get_functions_query(self):
        function_names = [f.name for f in self.get_govt_functions()]
        ckan_tag_names = [re.sub("[^\w -]", "", n) for n in function_names]
        if len(ckan_tag_names) == 0:
            # We select datasets with no functions rather than datasets
            # with any function (e.g. a blank query) because this query
            # is intended to restrict datasets to matching functions.
            return none_selected_query("vocab_functions")
        else:
            options = ['+vocab_functions:"%s"' % n for n in ckan_tag_names]
            return "+(%s)" % " OR ".join(options)

    def get_contributed_datasets(self):
        # We use an OrderedDict like an Ordered Set to ensure we include each
        # match just once, and at the highest rank it came up in.
        datasets = OrderedDict()

        fq_org = '-organization:"national-treasury"'
        fq_group = '+(*:* NOT groups:["" TO *])'
        fq_year = self._get_financial_year_query()
        fq_sphere = '+vocab_spheres:"%s"' % self.government.sphere.slug
        fq_government = self._get_government_query()
        fq_functions = self._get_functions_query()
        fq_no_functions = none_selected_query("vocab_functions")
        queries = [
            (fq_org, fq_group, fq_year, fq_sphere, fq_government, fq_functions),
            (fq_org, fq_group, fq_sphere, fq_government, fq_functions),
            (fq_org, fq_group, fq_year, fq_sphere, fq_functions),
            (fq_org, fq_group, fq_sphere, fq_functions),
            (fq_org, fq_group, fq_functions),
            (fq_org, fq_group, fq_no_functions),
        ]
        for query in queries:
            params = {"q": "", "fq": "".join(query), "rows": 1000}
            response = ckan.action.package_search(**params)
            logger.info(
                "query %s\nto ckan returned %d results",
                pformat(params),
                len(response["results"]),
            )
            for package in response["results"]:
                if package["name"] not in datasets:
                    dataset = Dataset.from_package(package)
                    datasets[package["name"]] = dataset
        return datasets.values()

    def get_estimates_of_econ_classes_expenditure_dataset(self, level=3):
        if (
            self._estimates_of_econ_classes_expenditure_dataset.get(level, None)
            is not None
        ):
            return self._estimates_of_econ_classes_expenditure_dataset[level]
        query = {
            "q": "",
            "fq": "".join(
                [
                    '+organization:"national-treasury"',
                    '+groups:"estimates-of-%s-expenditure"'
                    % self.government.sphere.slug,
                    '+vocab_financial_years:"%s"' % self.get_financial_year().slug,
                    '+vocab_dimensions:"Economic classification %d"' % level,
                ]
            ),
            "rows": 1000,
            "rows": 1000,
        }
        response = ckan.action.package_search(**query)
        logger.info(
            "query %s\nreturned %d results", pformat(query), len(response["results"])
        )
        if response["results"]:
            package = response["results"][0]
            self._estimates_of_econ_classes_expenditure_dataset[
                level
            ] = Dataset.from_package(package)
            return self._estimates_of_econ_classes_expenditure_dataset[level]
        else:
            return None

    def get_adjusted_estimates_expenditure_dataset(self):
        if self._adjusted_estimates_of_expenditure_dataset is not None:
            return self._adjusted_estimates_of_expenditure_dataset
        query = {
            "q": "",
            "fq": "".join(
                [
                    '+organization:"national-treasury"',
                    '+groups:"adjusted-estimates-of-%s-expenditure"'
                    % self.government.sphere.slug,
                    '+vocab_financial_years:"%s"' % self.get_financial_year().slug,
                ]
            ),
            "rows": 1000,
        }
        response = ckan.action.package_search(**query)
        logger.info(
            "query %s\nreturned %d results", pformat(query), len(response["results"])
        )
        if response["results"]:
            package = response["results"][0]
            self._adjusted_estimates_of_expenditure_dataset = Dataset.from_package(
                package
            )
            return self._adjusted_estimates_of_expenditure_dataset
        else:
            return None

    def get_estimates_of_subprogramme_expenditure_dataset(self):
        """
        Gets the dataset that should have this department's budget data
        for this year down to sub-programme level
        """
        if self._estimates_of_subprogramme_expenditure_dataset is not None:
            return self._estimates_of_subprogramme_expenditure_dataset
        query = {
            "q": "",
            "fq": "".join(
                [
                    '+organization:"national-treasury"',
                    '+groups:"estimates-of-%s-expenditure"'
                    % self.government.sphere.slug,
                    '+vocab_financial_years:"%s"' % self.get_financial_year().slug,
                    '+vocab_dimensions:"Sub-programme"',
                ]
            ),
            "rows": 1000,
        }
        response = ckan.action.package_search(**query)
        if response["results"]:
            package = response["results"][0]
            self._estimates_of_subprogramme_expenditure_dataset = Dataset.from_package(
                package
            )
            return self._estimates_of_subprogramme_expenditure_dataset
        else:
            return None

    def get_expenditure_over_time(self):
        cpi_year_slug, cpi_resource_id = Dataset.get_latest_cpi_resource()
        base_year = get_base_year(cpi_year_slug)
        financial_year_start = self.get_financial_year().get_starting_year()
        financial_year_start_int = int(financial_year_start)
        financial_year_starts = [
            str(y)
            for y in range(financial_year_start_int - 4, financial_year_start_int + 3)
        ]
        expenditure = {
            "base_financial_year": FinancialYear.slug_from_year_start(str(base_year)),
            "nominal": [],
            "real": [],
        }

        dataset = self.get_estimates_of_econ_classes_expenditure_dataset()
        if not dataset:
            return None
        openspending_api = dataset.get_openspending_api()
        cuts = []
        if self.government.sphere.slug == "provincial":
            cuts.append(openspending_api.get_geo_ref() + ':"%s"' % self.government.name)
        drilldowns = [
            openspending_api.get_financial_year_ref(),
            openspending_api.get_phase_ref(),
            openspending_api.get_department_name_ref(),
        ]
        budget_results = openspending_api.aggregate(cuts=cuts, drilldowns=drilldowns)
        result = openspending_api.filter_dept(budget_results, self.name)

        if result["cells"]:
            cpi = get_cpi()
            for idx, financial_year_start in enumerate(financial_year_starts):
                phase = TRENDS_AND_ESTIMATES_PHASES[idx]
                cell = [
                    c
                    for c in result["cells"]
                    if c[openspending_api.get_financial_year_ref()]
                    == int(financial_year_start)
                    and c[openspending_api.get_phase_ref()] == phase
                ][0]
                nominal = cell["value.sum"]
                expenditure["nominal"].append(
                    {
                        "financial_year": FinancialYear.slug_from_year_start(
                            financial_year_start
                        ),
                        "amount": nominal,
                        "phase": phase,
                    }
                )
                expenditure["real"].append(
                    {
                        "financial_year": FinancialYear.slug_from_year_start(
                            financial_year_start
                        ),
                        "amount": int(
                            (Decimal(nominal) / cpi[financial_year_start]["index"])
                            * 100
                        ),
                        "phase": phase,
                    }
                )

            return {
                "expenditure": expenditure,
                "dataset_detail_page": dataset.get_url_path(),
            }
        else:
            logger.warning(
                "Missing expenditure data for %r budget year %s",
                cuts,
                self.get_financial_year().slug,
            )
            return None

    def get_adjusted_budget_summary(self):
        dataset = self.get_adjusted_estimates_expenditure_dataset()
        if not dataset:
            return None
        openspending_api = dataset.get_openspending_api()
        if not openspending_api:
            return None

        result_for_type_and_total = openspending_api.aggregate(
            cuts=[
                openspending_api.get_financial_year_ref()
                + ":"
                + self.get_financial_year().get_starting_year()
            ],
            drilldowns=[
                openspending_api.get_adjustment_kind_ref(),
                openspending_api.get_phase_ref(),
                openspending_api.get_programme_name_ref(),
                openspending_api.get_department_name_ref(),
            ],
            order=[openspending_api.get_adjustment_kind_ref()],
        )

        result_for_type_and_total = openspending_api.filter_dept(
            result_for_type_and_total, self.name
        )

        filtered_cells = openspending_api.filter_by_ref_exclusion(
            result_for_type_and_total["cells"],
            openspending_api.get_programme_name_ref(),
            DIRECT_CHARGE_NRF,
        )

        cells_for_type_and_total = openspending_api.aggregate_by_refs(
            [
                openspending_api.get_adjustment_kind_ref(),
                openspending_api.get_phase_ref(),
            ],
            filtered_cells,
        )

        if not cells_for_type_and_total:
            return None
        total_voted, total_adjusted = self._get_total_budget_adjustment(
            openspending_api, cells_for_type_and_total
        )

        dept_aggregate_url = openspending_api.aggregate_url(
            cuts=[
                openspending_api.get_financial_year_ref()
                + ":"
                + self.get_financial_year().get_starting_year(),
                openspending_api.get_department_name_ref() + ":" + self.name,
            ],
            drilldowns=openspending_api.get_all_drilldowns(),
        )

        return {
            "by_type": self._get_adjustments_by_type(
                openspending_api, cells_for_type_and_total
            ),
            "total_change": {
                "amount": total_adjusted,
                "percentage": (float(total_adjusted) / float(total_voted)) * 100,
            },
            "econ_classes": self._get_adjustments_by_econ_class(openspending_api),
            "programmes": self._get_adjustments_by_programme(openspending_api),
            "virements": self._get_budget_virements(
                openspending_api, dataset, total_voted
            ),
            "special_appropriation": self._get_budget_special_appropriations(
                openspending_api, total_voted
            ),
            "direct_charges": self._get_budget_direct_charges(openspending_api),
            "department_data_csv": csv_url(dept_aggregate_url),
            "dataset_detail_page": dataset.get_url_path(),
        }

    def _get_adjustments_by_type(self, openspending_api, cells):
        budget_phase_ref = openspending_api.get_phase_ref()
        adjustment_kind_ref = openspending_api.get_adjustment_kind_ref()

        def filter_by_type(cell):
            types = [
                "Adjustments - Announced in the budget speech",
                "Adjustments - Declared unspent funds",
                "Adjustments - Emergency funding",
                "Adjustments - Roll-overs",
                "Adjustments - Self-financing",
                "Adjustments - Shifting of functions between votes",
                "Adjustments - Shifting of functions within the vote",
                "Adjustments - Significant and unforeseeable economic and financial events",
                "Adjustments - Unforeseeable/unavoidable",
                "Adjustments - Virements and shifts due to savings",
            ]

            whitelist = {"Adjusted appropriation": types}
            whitelist_keys = whitelist.keys()
            phase = cell[budget_phase_ref]
            descript = cell[adjustment_kind_ref]
            if phase in whitelist_keys:
                if descript in whitelist[phase]:
                    return True
            return False

        cells_by_type = [c for c in cells if filter_by_type(c)]
        by_type = []
        for cell in cells_by_type:
            name = cell[adjustment_kind_ref]
            name = name.replace("Adjustments - ", "")
            if cell["value.sum"]:
                by_type.append(
                    {"name": name, "amount": cell["value.sum"], "type": "kind"}
                )

        return by_type if by_type else None

    def _get_adjustments_by_programme(self, openspending_api):
        result_for_programmes = openspending_api.aggregate(
            cuts=[
                openspending_api.get_financial_year_ref()
                + ":"
                + self.get_financial_year().get_starting_year(),
                openspending_api.get_department_name_ref() + ':"' + self.name + '"',
                openspending_api.get_adjustment_kind_ref()
                + ":"
                + '"Adjustments - Total adjustments"',
            ],
            drilldowns=[
                openspending_api.get_programme_name_ref(),
                openspending_api.get_phase_ref(),
                openspending_api.get_department_name_ref(),
            ],
            order=[openspending_api.get_programme_name_ref()],
        )
        result_for_programmes = openspending_api.filter_dept(
            result_for_programmes, self.name
        )

        programme_name_ref = openspending_api.get_programme_name_ref()
        cells_for_programmes = openspending_api.filter_by_ref_exclusion(
            result_for_programmes["cells"], programme_name_ref, DIRECT_CHARGE_NRF
        )
        programmes = [
            {"name": cell[programme_name_ref], "amount": cell["value.sum"]}
            for cell in cells_for_programmes
            if cell["value.sum"]
        ]
        return programmes if programmes else None

    def _get_adjustments_by_econ_class(self, openspending_api):
        result_for_econ_classes = openspending_api.aggregate(
            cuts=[
                openspending_api.get_financial_year_ref()
                + ":"
                + self.get_financial_year().get_starting_year(),
                openspending_api.get_adjustment_kind_ref()
                + ":"
                + '"Adjustments - Total adjustments"',
            ],
            drilldowns=[
                openspending_api.get_econ_class_2_ref(),
                openspending_api.get_econ_class_3_ref(),
                openspending_api.get_programme_name_ref(),
                openspending_api.get_department_name_ref(),
            ],
            order=[
                openspending_api.get_econ_class_2_ref(),
                openspending_api.get_econ_class_3_ref(),
            ],
        )

        result_for_econ_classes = openspending_api.filter_dept(
            result_for_econ_classes, self.name
        )

        econ_classes = dict()
        econ_class_2_ref = openspending_api.get_econ_class_2_ref()
        econ_class_3_ref = openspending_api.get_econ_class_3_ref()

        filtered_cells = openspending_api.filter_by_ref_exclusion(
            result_for_econ_classes["cells"],
            openspending_api.get_programme_name_ref(),
            DIRECT_CHARGE_NRF,
        )

        cells_for_econ_classes = openspending_api.aggregate_by_refs(
            [
                openspending_api.get_econ_class_2_ref(),
                openspending_api.get_econ_class_3_ref(),
            ],
            filtered_cells,
        )

        for cell in cells_for_econ_classes:
            new_econ_2_object = {
                "type": "economic_classification_3",
                "name": cell[econ_class_3_ref],
                "amount": cell["value.sum"],
            }
            if cell["value.sum"] != 0:
                if cell[econ_class_2_ref] not in econ_classes.keys():
                    econ_classes[cell[econ_class_2_ref]] = {
                        "type": "economic_classification_2",
                        "name": cell[econ_class_2_ref],
                        "items": [],
                    }
                econ_classes[cell[econ_class_2_ref]]["items"].append(new_econ_2_object)
        # sort by name
        name_func = lambda x: x["name"]
        for econ_2_name in list(
            econ_classes.keys()
        ):  # Copy keys because we're updating dict
            econ_classes[econ_2_name]["items"] = sorted(
                econ_classes[econ_2_name]["items"], key=name_func
            )
        econ_classes_list = sorted(econ_classes.values(), key=name_func)
        return econ_classes_list if econ_classes_list else None

    @staticmethod
    def _get_total_budget_adjustment(openspending_api, cells):
        if not cells:
            return None
        phase_ref = openspending_api.get_phase_ref()
        descript_ref = openspending_api.get_adjustment_kind_ref()
        total_adjusted, total_voted = None, None

        for cell in cells:
            if (
                cell[phase_ref] == "Adjusted appropriation"
                and cell[descript_ref] == "Adjustments - Total adjustments"
            ):
                total_adjusted = cell["value.sum"]
            if (
                cell[phase_ref] == "Voted (Main appropriation)"
                and cell[descript_ref] == "Total"
            ):
                total_voted = cell["value.sum"]

        if total_voted and not total_adjusted:
            total_adjusted = 0
        elif not (total_voted or total_adjusted):
            raise Exception("Could not calculate total change for department budget")

        return total_voted, total_adjusted

    def _get_budget_virements(self, openspending_api, dataset, total_voted):
        virements_resource = dataset.get_resource("CSV", name="Value of Virements")
        if virements_resource:
            sql = """
                    SELECT "Value of Virements" FROM "{}"
                    WHERE "department_name"='{}'
                    """.format(
                virements_resource["id"], self.name
            )
            params = {"sql": sql}
            result = requests.get(CKAN_DATASTORE_URL, params=params)
            result.raise_for_status()
            records = result.json()["result"]["records"]
            value = records[0]["Value of Virements"]

            virements = {
                "label": "Value of virements",
                "amount": int(value),
                "percentage": 100 * (float(value) / float(total_voted)),
            }
        else:
            result_for_virements = openspending_api.aggregate(
                cuts=[
                    openspending_api.get_financial_year_ref()
                    + ":"
                    + self.get_financial_year().get_starting_year(),
                    openspending_api.get_adjustment_kind_ref()
                    + ":"
                    + '"Adjustments - Virements and shifts due to savings"',
                ],
                drilldowns=openspending_api.get_all_drilldowns(),
            )

            result_for_virements = openspending_api.filter_dept(
                result_for_virements, self.name
            )
            cells_for_virements = openspending_api.filter_by_ref_exclusion(
                result_for_virements["cells"],
                openspending_api.get_programme_name_ref(),
                DIRECT_CHARGE_NRF,
            )
            total_positive_virement_change = 0
            for c in cells_for_virements:
                if c["value.sum"] > 0:
                    total_positive_virement_change += c["value.sum"]
            virements = {
                "label": "Value of virements and shifts due to savings",
                "amount": int(total_positive_virement_change),
                "percentage": 100
                * float(total_positive_virement_change)
                / float(total_voted),
            }
        return virements if virements else None

    def _get_budget_special_appropriations(self, openspending_api, total_voted):
        result_for_special_appropriations = openspending_api.aggregate(
            cuts=[
                openspending_api.get_financial_year_ref()
                + ":"
                + self.get_financial_year().get_starting_year(),
                openspending_api.get_adjustment_kind_ref()
                + ":"
                + '"Special appropriation"',
            ],
            drilldowns=[openspending_api.get_department_name_ref()],
        )
        result_for_special_appropriations = openspending_api.filter_dept(
            result_for_special_appropriations, self.name
        )

        total_special_appropriations = 0
        for cell in result_for_special_appropriations["cells"]:
            if cell["value.sum"]:
                total_special_appropriations += cell["value.sum"]

        if total_special_appropriations:
            return {
                "amount": total_special_appropriations,
                "percentage": (float(total_special_appropriations) / float(total_voted))
                * 100,
            }
        else:
            return None

    def _get_budget_direct_charges(self, openspending_api):
        result_for_direct_charges = openspending_api.aggregate(
            cuts=[
                openspending_api.get_financial_year_ref()
                + ":"
                + self.get_financial_year().get_starting_year(),
                openspending_api.get_programme_name_ref() + ":" + DIRECT_CHARGE_NRF,
            ],
            drilldowns=[
                openspending_api.get_phase_ref(),
                openspending_api.get_subprogramme_name_ref(),
                openspending_api.get_department_name_ref(),
                openspending_api.get_adjustment_kind_ref(),
            ],
            order=[openspending_api.get_subprogramme_name_ref()],
        )
        result_for_direct_charges = openspending_api.filter_dept(
            result_for_direct_charges, self.name
        )

        subprog_ref = openspending_api.get_subprogramme_name_ref()
        phase_ref = openspending_api.get_phase_ref()
        kind_ref = openspending_api.get_adjustment_kind_ref()
        subprog_dict = OrderedDict()

        for cell in result_for_direct_charges["cells"]:
            if cell[kind_ref] == "Adjustments - Total adjustments":
                subprog_dict[cell[subprog_ref]] = {
                    "amount": cell["value.sum"],
                    "label": cell[subprog_ref],
                }

        for subprog in subprog_dict.keys():
            for cell in result_for_direct_charges["cells"]:
                if cell[subprog_ref] == subprog:
                    if cell[phase_ref] == "Voted (Main appropriation)":
                        subprog_dict[subprog]["percentage"] = (
                            float(subprog_dict[subprog]["amount"])
                            / float(cell["value.sum"])
                        ) * 100

        return subprog_dict.values() if subprog_dict else None

    def get_all_budget_totals_by_year_and_phase(self):
        """ Returns the total for each year:phase combination from the expenditure time series dataset. """
        dataset = get_expenditure_time_series_dataset(self.government.sphere.slug)
        if not dataset:
            return None
        openspending_api = dataset.get_openspending_api()
        phase_ref = openspending_api.get_phase_ref()
        year_ref = openspending_api.get_financial_year_ref()

        total_budget_cuts = [
            openspending_api.get_adjustment_kind_ref() + ":" + '"Total"'
        ]
        total_budget_drilldowns = [
            year_ref,
            phase_ref,
            openspending_api.get_programme_name_ref(),
        ]
        total_budget_results = openspending_api.aggregate(
            cuts=total_budget_cuts, drilldowns=total_budget_drilldowns
        )
        total_budget_filtered = openspending_api.filter_by_ref_exclusion(
            total_budget_results["cells"],
            openspending_api.get_programme_name_ref(),
            DIRECT_CHARGE_NRF,
        )
        total_budget_aggregated = openspending_api.aggregate_by_refs(
            [year_ref, phase_ref], total_budget_filtered
        )

        total_budgets = {}
        for cell in total_budget_aggregated:
            if cell[phase_ref] not in total_budgets.keys():
                total_budgets[cell[phase_ref]] = {
                    cell[year_ref]: float(cell["value.sum"])
                }
            else:
                total_budgets[cell[phase_ref]][cell[year_ref]] = float(
                    cell["value.sum"]
                )

        return total_budgets

    def get_national_expenditure_treemap(self, financial_year_id, budget_phase):
        """ Returns a data object for each department, year and phase. Adds additional data required for the Treemap.
         From the Expenditure Time Series dataset. """
        # Take budget sphere, year and phase as positional arguments from URL
        # Output expenditure specific to sphere:year:phase scope, simple list of objects
        try:
            selected_phase = EXPENDITURE_TIME_SERIES_PHASE_MAPPING[budget_phase]
        except KeyError:
            raise Exception("An invalid phase was provided: {}".format(budget_phase))

        expenditure = []
        dataset = get_expenditure_time_series_dataset(self.government.sphere.slug)
        if not dataset:
            return None
        openspending_api = dataset.get_openspending_api()
        phase_ref = openspending_api.get_phase_ref()
        year_ref = openspending_api.get_financial_year_ref()

        # Add cuts: year and phase
        expenditure_cuts = [
            openspending_api.get_adjustment_kind_ref() + ":" + '"Total"',
            year_ref
            + ":"
            + "{}".format(FinancialYear.start_from_year_slug(financial_year_id)),
            phase_ref + ":" + '"{}"'.format(selected_phase),
        ]
        expenditure_drilldowns = [
            year_ref,
            phase_ref,
            openspending_api.get_department_name_ref(),
            openspending_api.get_programme_name_ref(),
        ]

        expenditure_results = openspending_api.aggregate(
            cuts=expenditure_cuts, drilldowns=expenditure_drilldowns
        )

        # Disaggregate and filter out any direct charge NRF programmes
        filtered_cells = openspending_api.filter_by_ref_exclusion(
            expenditure_results["cells"],
            openspending_api.get_programme_name_ref(),
            DIRECT_CHARGE_NRF,
        )

        # Re-aggregate by year:phase
        result_cells = openspending_api.aggregate_by_refs(
            [openspending_api.get_department_name_ref(), year_ref, phase_ref],
            filtered_cells,
        )

        total_budget = 0
        filtered_result_cells = []
        national_depts = Department.objects.filter(
            government__sphere__slug="national", is_vote_primary=True
        )

        dept = None
        for cell in result_cells:
            try:
                if year_ref in cell:
                    dept = national_depts.get(
                        government__sphere__financial_year__slug=FinancialYear.slug_from_year_start(
                            str(cell[year_ref])
                        ),
                        slug=slugify(cell[openspending_api.get_department_name_ref()]),
                    )
            except Department.DoesNotExist:
                logger.warning(
                    "Excluding: national {} {}".format(
                        cell[year_ref], cell[openspending_api.get_department_name_ref()]
                    )
                )
                continue

            total_budget += float(cell["value.sum"])
            cell["url"] = dept.get_preview_url_path() if dept else None
            filtered_result_cells.append(cell)

        for cell in filtered_result_cells:

            percentage_of_total = (
                float(cell["value.sum"]) / total_budget * 100
                if cell["value.sum"]
                else 0
            )

            name = (
                cell[openspending_api.get_department_name_ref()]
                if openspending_api.get_department_name_ref() in cell
                else ""
            )

            expenditure.append(
                {
                    "name": name,
                    "slug": slugify(name),
                    "amount": float(cell["value.sum"]),
                    "percentage_of_total": percentage_of_total,
                    "province": None,  # to keep a consistent schema
                    "url": cell["url"],
                }
            )

        return (
            {"data": {"items": expenditure, "total": total_budget}}
            if expenditure
            else None
        )

    def get_provincial_expenditure_treemap(self, financial_year_id, budget_phase):
        """ Returns a list of department objects nested in provinces. """
        # Take budget sphere, year and phase as positional arguments from URL
        # Output expenditure specific to sphere:year:phase scope, simple list of objects
        try:
            selected_phase = EXPENDITURE_TIME_SERIES_PHASE_MAPPING[budget_phase]
        except KeyError:
            raise Exception("An invalid phase was provided: {}".format(budget_phase))

        expenditure = []
        dataset = get_expenditure_time_series_dataset(self.government.sphere.slug)
        if not dataset:
            return None
        openspending_api = dataset.get_openspending_api()

        # Add cuts: year and phase
        expenditure_cuts = [
            openspending_api.get_adjustment_kind_ref() + ":" + '"Total"',
            openspending_api.get_financial_year_ref()
            + ":"
            + "{}".format(FinancialYear.start_from_year_slug(financial_year_id)),
            openspending_api.get_phase_ref() + ":" + '"{}"'.format(selected_phase),
        ]
        expenditure_drilldowns = [
            openspending_api.get_department_name_ref(),
            openspending_api.get_geo_ref(),
        ]

        expenditure_results = openspending_api.aggregate(
            cuts=expenditure_cuts, drilldowns=expenditure_drilldowns
        )

        total_budget = 0
        filtered_result_cells = []
        provincial_depts = Department.objects.filter(
            government__sphere__financial_year__slug=financial_year_id,
            government__sphere__slug="provincial",
            is_vote_primary=True,
        )

        for cell in expenditure_results["cells"]:
            try:
                dept = provincial_depts.get(
                    slug=slugify(cell[openspending_api.get_department_name_ref()]),
                    government__slug=slugify(cell[openspending_api.get_geo_ref()]),
                )
            except Department.DoesNotExist:
                logger.warning(
                    "Excluding: provincial {} {} {}".format(
                        financial_year_id,
                        cell[openspending_api.get_geo_ref()],
                        cell[openspending_api.get_department_name_ref()],
                    )
                )
                continue

            total_budget += float(cell["value.sum"])
            cell["url"] = dept.get_preview_url_path() if dept else None
            filtered_result_cells.append(cell)

        for cell in filtered_result_cells:
            expenditure.append(
                {
                    "name": cell[openspending_api.get_department_name_ref()],
                    "slug": slugify(cell[openspending_api.get_department_name_ref()]),
                    "amount": float(cell["value.sum"]),
                    "province": cell[openspending_api.get_geo_ref()],
                    "url": cell["url"],
                }
            )

        return (
            {"data": {"items": expenditure, "total": total_budget}}
            if expenditure
            else None
        )

    def get_expenditure_time_series_summary(self):
        cpi_year_slug, cpi_resource_id = Dataset.get_latest_cpi_resource()
        base_year = get_base_year(cpi_year_slug)
        financial_year_start = self.get_financial_year().get_starting_year()
        financial_year_start_int = int(financial_year_start)
        financial_year_starts = [
            str(y)
            for y in range(financial_year_start_int - 3, financial_year_start_int + 1)
        ]

        expenditure = {"nominal": [], "real": []}

        dataset = get_expenditure_time_series_dataset(self.government.sphere.slug)
        if not dataset:
            return None
        openspending_api = dataset.get_openspending_api()

        cuts = [
            openspending_api.get_adjustment_kind_ref() + ":" + '"Total"',
            openspending_api.get_geo_ref() + ":" + '"%s"' % self.government.name,
        ]
        drilldowns = [
            openspending_api.get_financial_year_ref(),
            openspending_api.get_phase_ref(),
            openspending_api.get_department_name_ref(),
            openspending_api.get_programme_name_ref(),
        ]
        budget_results = openspending_api.aggregate(cuts=cuts, drilldowns=drilldowns)
        result = openspending_api.filter_dept(budget_results, self.name)
        filtered_cells = openspending_api.filter_by_ref_exclusion(
            result["cells"],
            openspending_api.get_programme_name_ref(),
            DIRECT_CHARGE_NRF,
        )

        result_cells = openspending_api.aggregate_by_refs(
            [
                openspending_api.get_department_name_ref(),
                openspending_api.get_financial_year_ref(),
                openspending_api.get_phase_ref(),
            ],
            filtered_cells,
        )

        if result_cells:
            cpi = get_cpi()
            for financial_year_start in financial_year_starts:
                for phase in EXPENDITURE_TIME_SERIES_PHASES:
                    cells = [
                        c
                        for c in result_cells
                        if c[openspending_api.get_financial_year_ref()]
                        == int(financial_year_start)
                        and c[openspending_api.get_phase_ref()] == phase
                    ]
                    if cells:
                        cell = cells[0]
                        nominal = cell["value.sum"]
                        expenditure["nominal"].append(
                            {
                                "financial_year": FinancialYear.slug_from_year_start(
                                    financial_year_start
                                ),
                                "amount": nominal,
                                "phase": phase,
                            }
                        )
                        expenditure["real"].append(
                            {
                                "financial_year": FinancialYear.slug_from_year_start(
                                    financial_year_start
                                ),
                                "amount": int(
                                    (
                                        Decimal(nominal)
                                        / cpi[financial_year_start]["index"]
                                    )
                                    * 100
                                ),
                                "phase": phase,
                            }
                        )

            missing_phases_count = {}
            found = False
            for fiscal_year in financial_year_starts:
                for fiscal_phase in EXPENDITURE_TIME_SERIES_PHASES:
                    for fiscal_type in expenditure:
                        for item in expenditure[fiscal_type]:
                            found = False
                            if (
                                item["financial_year"]
                                == FinancialYear.slug_from_year_start(fiscal_year)
                                and item["phase"] == fiscal_phase
                            ):
                                found = True
                                break
                        if not found:
                            expenditure[fiscal_type].append(
                                {
                                    "financial_year": FinancialYear.slug_from_year_start(
                                        fiscal_year
                                    ),
                                    "phase": fiscal_phase,
                                    "amount": None,
                                }
                            )
                            if fiscal_year not in missing_phases_count:
                                missing_phases_count[fiscal_year] = 1
                            else:
                                missing_phases_count[fiscal_year] += 1

            expenditure["base_financial_year"] = FinancialYear.slug_from_year_start(
                str(base_year)
            )

            # Generate notices if applicable
            no_data_for_years = []
            no_dept_for_years = []
            notices = []
            for year, count in missing_phases_count.items():
                # 8 because 4 phases real and nominal
                if count != 8:
                    # All phases for a given year must be missing before starting any checks
                    continue
                single_year_cuts = [
                    openspending_api.get_adjustment_kind_ref() + ":" + '"Total"',
                    openspending_api.get_financial_year_ref() + ":" + year,
                ]
                single_year_budget_results = openspending_api.aggregate(
                    cuts=single_year_cuts
                )

                if single_year_budget_results["cells"]:
                    value_sum = single_year_budget_results["cells"][0]["value.sum"]
                    if value_sum is not None and value_sum > 0:
                        # dept did not exist, since there is data for other departments
                        no_dept_for_years.append(year)
                    else:
                        # no data for this fiscal year, so data hasn't been published yet
                        no_data_for_years.append(year)
                else:
                    # no data for this fiscal year, so data hasn't been published yet
                    no_data_for_years.append(year)

            if no_data_for_years:
                notice_string = "Please note that the data for"
                no_data_for_years.sort()
                if len(no_data_for_years) == 1:
                    notice_string += " {}".format(no_data_for_years[0])
                elif len(no_data_for_years) == 2:
                    notice_string += " {}".format(" and ".join(no_data_for_years))
                else:
                    notice_string += " {}".format(", ".join(no_data_for_years[:-1]))
                    notice_string += " and {}".format(no_data_for_years[-1])
                notice_string += " has not been published on vulekamali."
                notices.append(notice_string)

            if no_dept_for_years:
                notices.append(
                    "This department did not exist for some years displayed."
                )

            return {
                "notices": notices,
                "expenditure": expenditure,
                "dataset_detail_page": dataset.get_url_path(),
            }
        else:
            logger.warning(
                "Missing expenditure time series data for %r budget year %s",
                cuts,
                self.get_financial_year().slug,
            )
            return None

    def get_expenditure_time_series_by_programme(self):
        financial_year_start = self.get_financial_year().get_starting_year()
        financial_year_start_int = int(financial_year_start)
        year_ints = range(financial_year_start_int - 3, financial_year_start_int + 1)
        financial_year_starts = [str(y) for y in year_ints]

        programmes = {}

        dataset = get_expenditure_time_series_dataset(self.government.sphere.slug)
        if not dataset:
            return None
        openspending_api = dataset.get_openspending_api()

        cuts = [
            openspending_api.get_adjustment_kind_ref() + ":" + '"Total"',
            openspending_api.get_geo_ref() + ":" + '"%s"' % self.government.name,
        ]
        drilldowns = [
            openspending_api.get_financial_year_ref(),
            openspending_api.get_phase_ref(),
            openspending_api.get_department_name_ref(),
            openspending_api.get_programme_name_ref(),
        ]
        budget_results = openspending_api.aggregate(cuts=cuts, drilldowns=drilldowns)
        result = openspending_api.filter_dept(budget_results, self.name)

        if result["cells"]:
            prog_names = [
                cell[openspending_api.get_programme_name_ref()]
                for cell in result["cells"]
            ]
            prog_names = set(prog_names)
            for financial_year_start in financial_year_starts:
                for phase in EXPENDITURE_TIME_SERIES_PHASES:
                    for prog_name in prog_names:
                        cells = [
                            c
                            for c in result["cells"]
                            if c[openspending_api.get_financial_year_ref()]
                            == int(financial_year_start)
                            and c[openspending_api.get_phase_ref()] == phase
                            and c[openspending_api.get_programme_name_ref()]
                            == prog_name
                        ]
                        if cells:
                            cell = cells[0]
                            nominal = cell["value.sum"]
                            try:
                                programmes[prog_name]
                            except KeyError:
                                programmes[prog_name] = {"name": prog_name, "items": []}
                            programmes[prog_name]["items"].append(
                                {
                                    "financial_year": FinancialYear.slug_from_year_start(
                                        financial_year_start
                                    ),
                                    "amount": nominal,
                                    "phase": phase,
                                }
                            )

            found = False
            missing_phases_count = {}
            for fiscal_year in financial_year_starts:
                for fiscal_phase in EXPENDITURE_TIME_SERIES_PHASES:
                    for program in programmes:
                        for item in programmes[program]["items"]:
                            found = False
                            if (
                                item["financial_year"]
                                == FinancialYear.slug_from_year_start(fiscal_year)
                                and item["phase"] == fiscal_phase
                            ):
                                found = True
                                break
                        if not found:
                            programmes[program]["items"].append(
                                {
                                    "financial_year": FinancialYear.slug_from_year_start(
                                        fiscal_year
                                    ),
                                    "phase": fiscal_phase,
                                    "amount": None,
                                }
                            )
                            if fiscal_year not in missing_phases_count:
                                missing_phases_count[fiscal_year] = {program: 1}
                            else:
                                if (
                                    program
                                    not in missing_phases_count[fiscal_year].keys()
                                ):
                                    missing_phases_count[fiscal_year][program] = 1
                                else:
                                    missing_phases_count[fiscal_year][program] += 1

            no_prog_for_years = False
            notices = []
            for year, progs in missing_phases_count.items():
                if no_prog_for_years:
                    break
                for p, count in progs.items():
                    if no_prog_for_years:
                        break
                    if count == 4:
                        single_year_cuts = [
                            openspending_api.get_adjustment_kind_ref()
                            + ":"
                            + '"Total"',
                            openspending_api.get_financial_year_ref() + ":" + year,
                        ]
                        single_year_budget_results = openspending_api.aggregate(
                            cuts=single_year_cuts
                        )

                        if single_year_budget_results["cells"]:
                            value_sum = single_year_budget_results["cells"][0][
                                "value.sum"
                            ]
                            if value_sum is not None and value_sum > 0:
                                # prog did not exist, since there is data for other programmes
                                no_prog_for_years = True

            if no_prog_for_years:
                notices.append(
                    "One or more programmes did not exist for some years displayed."
                )

            return {
                "notices": notices,
                "programmes": programmes.values(),  # FIXME need to add sorting with python3
                "dataset_detail_page": dataset.get_url_path(),
            }
        else:
            logger.warning(
                "Missing expenditure time series data for %r budget year %s",
                cuts,
                self.get_financial_year().slug,
            )
            return None


def __str__(self):
    return "<%s %s>" % (self.__class__.__name__, self.get_url_path())


class GovtFunction(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = AutoSlugField(
        populate_from="name", max_length=200, always_update=True, unique=True
    )

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, self.slug)


class Programme(models.Model):
    organisational_unit = "programme"
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="programmes"
    )
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from="name", max_length=200, always_update=True)
    programme_number = models.IntegerField()
    govt_functions = models.ManyToManyField(GovtFunction)

    class Meta:
        unique_together = (
            ("department", "slug"),
            ("department", "name"),
            ("department", "programme_number"),
        )

        ordering = ["programme_number"]

    def get_url_path(self):
        return "%s/programmes/%s" % (self.department.get_url_path(), self.slug)

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, self.get_url_path())


class InfrastructureProjectPart(models.Model):
    administration_type = models.CharField(max_length=255)
    government_institution = models.CharField(max_length=255)
    sector = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255)
    project_description = models.TextField()
    nature_of_investment = models.CharField(max_length=255)
    infrastructure_type = models.CharField(max_length=255)
    current_project_stage = models.CharField(max_length=255)
    sip_category = models.CharField(max_length=255)
    br_featured = models.CharField(max_length=255)
    featured = models.BooleanField()
    budget_phase = models.CharField(max_length=255)
    project_slug = models.CharField(max_length=255)
    amount_rands = models.BigIntegerField(blank=True, null=True, default=None)
    financial_year = models.CharField(max_length=4)
    project_value_rands = models.BigIntegerField(default=0)
    provinces = models.CharField(max_length=510, default="")
    gps_code = models.CharField(max_length=255, default="")

    # PPP fields
    partnership_type = models.CharField(max_length=255, null=True, blank=True)
    date_of_close = models.CharField(max_length=255, null=True, blank=True)
    duration = models.CharField(max_length=255, null=True, blank=True)
    financing_structure = models.CharField(max_length=255, null=True, blank=True)
    project_value_rand_million = models.CharField(max_length=255, null=True, blank=True)
    form_of_payment = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "National infrastructure project part"

    def __str__(self):
        return "{} ({} {})".format(
            self.project_slug, self.budget_phase, self.financial_year
        )

    def get_url_path(self):
        return "/infrastructure-projects/{}".format(self.project_slug)

    def get_absolute_url(self):
        return reverse("infrastructure-projects", args=[self.project_slug])

    def calculate_projected_expenditure(self):
        """ Calculate sum of predicted amounts from a list of records """
        projected_records_for_project = InfrastructureProjectPart.objects.filter(
            budget_phase="MTEF", project_slug=self.project_slug
        )
        projected_expenditure = 0
        for project in projected_records_for_project:
            projected_expenditure += float(project.amount_rands or 0.0)
        return projected_expenditure

    @staticmethod
    def _parse_coordinate(coordinate):
        """ Expects a single set of coordinates (lat, long) split by a comma """
        if not isinstance(coordinate, str):
            raise TypeError("Invalid type for coordinate parsing")
        lat_long = [float(x) for x in coordinate.split(",")]
        cleaned_coordinate = {"latitude": lat_long[0], "longitude": lat_long[1]}
        return cleaned_coordinate

    @classmethod
    def clean_coordinates(cls, raw_coordinate_string):
        cleaned_coordinates = []
        try:
            if "and" in raw_coordinate_string:
                list_of_coordinates = raw_coordinate_string.split("and")
                for coordinate in list_of_coordinates:
                    cleaned_coordinates.append(cls._parse_coordinate(coordinate))
            elif "," in raw_coordinate_string:
                cleaned_coordinates.append(cls._parse_coordinate(raw_coordinate_string))
            else:
                logger.warning("Invalid co-ordinates: {}".format(raw_coordinate_string))
        except Exception as e:
            logger.warning(
                "Caught Exception '{}' for co-ordinates {}".format(
                    e, raw_coordinate_string
                )
            )
        return cleaned_coordinates

    @staticmethod
    def _get_province_from_coord(coordinate):
        """ Expects a cleaned coordinate """
        key = f"coordinate province {coordinate['latitude']}, {coordinate['longitude']}"
        province_name = cache.get(key, default="cache-miss")
        if province_name == "cache-miss":
            logger.info(f"Coordinate Province Cache MISS for coordinate {key}")
            params = {"type": "PR"}
            province_result = requests.get(
                MAPIT_POINT_API_URL.format(
                    coordinate["longitude"], coordinate["latitude"]
                ),
                params=params,
            )
            province_result.raise_for_status()
            r = province_result.json()
            list_of_objects_returned = list(r.values())
            if len(list_of_objects_returned) > 0:
                province_name = list_of_objects_returned[0]["name"]
            else:
                province_name = None
            cache.set(key, province_name)
        else:
            logger.info(f"Coordinate Province Cache HIT for coordinate {key}")
        return province_name

    @staticmethod
    def _get_province_from_project_name(project_name):
        """ Searches name of project for province name or abbreviation """
        project_name_slug = slugify(project_name)
        new_dict = {}
        for prov_name in prov_abbrev.keys():
            new_dict[prov_name] = slugify(prov_name)
        for name, slug in new_dict.items():
            if slug in project_name_slug:
                return name
        return None

    @classmethod
    def get_provinces(cls, cleaned_coordinates=None, project_name=""):
        """ Returns a list of provinces based on values in self.coordinates """
        provinces = set()
        if cleaned_coordinates:
            for c in cleaned_coordinates:
                province = cls._get_province_from_coord(c)
                if province:
                    provinces.add(province)
                else:
                    logger.warning(
                        "Couldn't find GPS co-ordinates for infrastructure project '{}' on MapIt: {}".format(
                            project_name, c
                        )
                    )
        else:
            province = cls._get_province_from_project_name(project_name)
            if province:
                logger.info("Found province {} in project name".format(province))
                provinces.add(province)
        return list(provinces)

    @staticmethod
    def _build_expenditure_item(project):
        return {
            "year": project.financial_year,
            "amount": project.amount_rands,
            "budget_phase": project.budget_phase,
        }

    def build_complete_expenditure(self):
        complete_expenditure = []
        projects = InfrastructureProjectPart.objects.filter(
            project_slug=self.project_slug
        )
        for project in projects:
            complete_expenditure.append(self._build_expenditure_item(project))
        return complete_expenditure


prov_keys = prov_abbrev.keys()
prov_choices = tuple([(prov_key, prov_key) for prov_key in prov_keys])


class Event(models.Model):
    start_date = models.DateField(default=datetime.now)
    date = models.CharField(max_length=255)
    type = models.CharField(
        max_length=255,
        choices=(
            ("hackathon", "hackathon"),
            ("dataquest", "dataquest"),
            ("cid", "cid"),
            ("gift-dataquest", "gift-dataquest"),
        ),
    )
    province = models.CharField(max_length=255, choices=prov_choices)
    where = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    notes_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    rsvp_url = models.URLField(blank=True, null=True)
    presentation_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=255,
        default="upcoming",
        choices=(("upcoming", "upcoming"), ("past", "past")),
    )

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return "{} {} ({} {})".format(self.type, self.date, self.where, self.province)

    def get_absolute_url(self):
        return reverse("events")


class VideoLanguage(SortableMixin):
    label = models.CharField(max_length=255)
    youtube_id = models.CharField(max_length=255, null=True, blank=True)
    video = models.ForeignKey("Video", null=True, blank=True, on_delete=models.SET_NULL)
    video_language_order = models.PositiveIntegerField(
        default=0, editable=False, db_index=True
    )

    class Meta:
        ordering = ["video_language_order"]

    def __str__(self):
        return self.label


class Video(SortableMixin):
    title_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=510)
    video_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        ordering = ["video_order"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("videos")


class FAQ(SortableMixin):
    title = models.CharField(max_length=1024)
    content = RichTextField()
    the_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ["the_order"]


class Quarter(models.Model):
    number = models.IntegerField(unique=True)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return "Quarter %d" % self.number


def irm_snapshot_file_path(instance, filename):
    extension = filename.split(".")[-1]
    return (
        f"irm-snapshots/{uuid.uuid4()}/"
        f"{instance.sphere.financial_year.slug}-Q{instance.quarter.number}-"
        f"{instance.sphere.slug}-taken-{instance.date_taken.isoformat()[:18]}.{extension}"
    )


class IRMSnapshot(models.Model):
    """
    This represents a particular snapshot from the Infrastructure Reporting Model
    (IRM) database
    """

    sphere = models.ForeignKey(Sphere, on_delete=models.CASCADE)
    quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE)
    date_taken = models.DateTimeField()
    file = models.FileField(upload_to=irm_snapshot_file_path)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        ordering = ["sphere__financial_year__slug", "quarter__number"]
        verbose_name = "IRM Snapshot"
        unique_together = ["sphere", "quarter"]

    def __str__(self):
        return (
            f"{self.sphere.name} "
            f"{self.sphere.financial_year.slug} Q{self.quarter.number} "
            f"taken {self.date_taken.isoformat()[:18]}"
        )


class InfraProject(models.Model):
    """This represents a project, grouping its snapshots"""

    IRM_project_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = "Infrastructure project"

    def __str__(self):
        if self.project_snapshots.count():
            return self.project_snapshots.latest().name
        else:
            return "IRM project ID %d (no snapshots loaded)" % self.IRM_project_id

    def get_slug(self):
        return slugify(
            "{0} {1}".format(
                self.project_snapshots.latest().name,
                self.project_snapshots.latest().province,
            )
        )

    def get_absolute_url(self):
        args = [self.pk, self.get_slug()]
        return reverse("infra-project-detail", args=args)

    @property
    def csv_download_url(self):
        return reverse(
            "infra-project-detail-csv-download",
            args=(self.id, self.get_slug()),
        )


class InfraProjectSnapshot(models.Model):
    """This represents a snapshot of a project, as it occurred in an IRM snapshot"""

    irm_snapshot = models.ForeignKey(
        IRMSnapshot, on_delete=models.CASCADE, related_name="project_snapshots"
    )
    project = models.ForeignKey(
        InfraProject, on_delete=models.CASCADE, related_name="project_snapshots"
    )
    project_number = models.CharField(max_length=1024, blank=True, null=True)
    name = models.CharField(max_length=1024, blank=True, null=True)
    department = models.CharField(max_length=1024, blank=True, null=True)
    sector = models.CharField(max_length=1024, blank=True, null=True)
    province = models.CharField(max_length=1024, blank=True, null=True)
    local_municipality = models.CharField(max_length=1024, blank=True, null=True)
    district_municipality = models.CharField(max_length=1024, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=1024, blank=True, null=True)
    budget_programme = models.CharField(max_length=1024, blank=True, null=True)
    primary_funding_source = models.CharField(max_length=1024, blank=True, null=True)
    nature_of_investment = models.CharField(max_length=1024, blank=True, null=True)
    funding_status = models.CharField(max_length=1024, blank=True, null=True)
    program_implementing_agent = models.CharField(
        max_length=1024, blank=True, null=True
    )
    principle_agent = models.CharField(max_length=1024, blank=True, null=True)
    main_contractor = models.CharField(max_length=1024, blank=True, null=True)
    other_parties = models.TextField(blank=True, null=True)

    # Dates
    start_date = models.DateField(blank=True, null=True)
    estimated_construction_start_date = models.DateField(blank=True, null=True)
    estimated_completion_date = models.DateField(blank=True, null=True)
    contracted_construction_end_date = models.DateField(blank=True, null=True)
    estimated_construction_end_date = models.DateField(blank=True, null=True)

    # Budgets and spending
    total_professional_fees = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    total_construction_costs = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    variation_orders = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    estimated_total_project_cost = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    expenditure_from_previous_years_professional_fees = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    expenditure_from_previous_years_construction_costs = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    expenditure_from_previous_years_total = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    project_expenditure_total = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    main_appropriation_professional_fees = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    adjusted_appropriation_professional_fees = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    main_appropriation_construction_costs = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    adjusted_appropriation_construction_costs = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    main_appropriation_total = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    adjusted_appropriation_total = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    actual_expenditure_q1 = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    actual_expenditure_q2 = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    actual_expenditure_q3 = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    actual_expenditure_q4 = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        ordering = [
            "irm_snapshot__sphere__financial_year__slug",
            "irm_snapshot__quarter__number",
        ]
        get_latest_by = "irm_snapshot"
        verbose_name = "Infrastructure project snapshot"
        unique_together = ["irm_snapshot", "project"]

    @property
    def government(self):
        if self.irm_snapshot.sphere.slug == "national":
            return "South Africa"
        elif self.irm_snapshot.sphere.slug == "provincial":
            return self.province
        else:
            raise Exception(f"Unexpected sphere {self.irm_snapshot.sphere}")

    @property
    def government_label(self):
        if self.irm_snapshot.sphere.slug == "national":
            return "national"
        elif self.irm_snapshot.sphere.slug == "provincial":
            return self.province
        else:
            raise Exception(f"Unexpected sphere {self.irm_snapshot.sphere}")


    def __str__(self):
        return self.name


# https://stackoverflow.com/questions/35633037/search-for-document-in-solr-where-a-multivalue-field-is-either-empty
# -or-has-a-sp
def none_selected_query(vocab_name):
    """Match items where none of the options in a custom vocab tag is selected"""
    return '+(*:* NOT %s:["" TO *])' % vocab_name


def extras_set(extras, key, value):
    for extra in extras:
        if extra["key"] == key:
            extra["value"] = value
            break


def resource_name(department):
    return "Vote %d - %s" % (department.vote_number, department.name)


def get_base_year(cpi_year_slug):
    return int(cpi_year_slug[:4]) - 1


def get_cpi():
    cpi_year_slug, cpi_resource_id = Dataset.get_latest_cpi_resource()
    base_year = get_base_year(cpi_year_slug)

    sql = """
    SELECT "Year", "CPI" FROM "{}"
    ORDER BY "Year"
    """.format(
        cpi_resource_id
    )
    params = {"sql": sql}
    result = requests.get(CKAN_DATASTORE_URL, params=params)
    result.raise_for_status()
    cpi = result.json()["result"]["records"]
    base_year_index = None
    for idx, cell in enumerate(cpi):
        financial_year_start = cell["Year"][:4]
        cell["financial_year_start"] = financial_year_start
        if financial_year_start == str(base_year):
            base_year_index = idx
            cell["index"] = 100
    for idx in range(base_year_index - 1, -1, -1):
        cpi[idx]["index"] = cpi[idx + 1]["index"] / (1 + Decimal(cpi[idx + 1]["CPI"]))
    for idx in range(base_year_index + 1, len(cpi)):
        cpi[idx]["index"] = cpi[idx - 1]["index"] * (1 + Decimal(cpi[idx]["CPI"]))
    cpi_dict = {}
    for cell in cpi:
        cpi_dict[cell["financial_year_start"]] = cell
    return cpi_dict


def get_vocab_map():
    vocab_map = {}
    for vocab in ckan.action.vocabulary_list():
        vocab_map[vocab["name"]] = vocab["id"]
    return vocab_map


def csv_url(aggregate_url):
    querystring = "?api_url=" + quote(aggregate_url)
    csv_url = reverse("openspending_csv") + querystring
    if len(csv_url) > URL_LENGTH_LIMIT:
        raise Exception(
            "Generated URL exceeds max length of %s. "
            "Some browsers may no longer be able to interpret the URL."
            % URL_LENGTH_LIMIT
        )
    return csv_url
