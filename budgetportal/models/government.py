from autoslug import AutoSlugField
from budgetportal.datasets import Dataset, get_expenditure_time_series_dataset
from collections import OrderedDict
from decimal import Decimal
from django.conf import settings
from django.db import models
from partial_index import PartialIndex
from pprint import pformat
from slugify import slugify
from urllib.parse import quote
import logging
from django.urls import reverse
import requests
from constance import config
from django.core.exceptions import MultipleObjectsReturned, ValidationError

logger = logging.getLogger(__name__)
ckan = settings.CKAN

NATIONAL_SLUG = "national"
PROVINCIAL_SLUG = "provincial"
SPHERE_SLUG_CHOICES = [
    (
        NATIONAL_SLUG,
        "National",
    ),
    (
        PROVINCIAL_SLUG,
        "Provincial",
    ),
]

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

PFMA_CHOICES = [
    ("1", "1"),
    ("2", "2"),
    ("3A", "3A"),
    ("3B", "3B"),
    ("NL", "Not listed"),
]

FUNCTIONGROUP1_CHOICES = (
    ("GPS", "General public services"),
    ("ED", "Economic development"),
    ("LAC", "Learning and culture"),
    ("SD", "Social development"),
    ("PAS", "Peace and security"),
    ("CD", "Community development"),
    ("H", "Health"),
)

DIRECT_CHARGE_NRF = "Direct charge against the National Revenue Fund"

URL_LENGTH_LIMIT = 2000

CKAN_DATASTORE_URL = settings.CKAN_URL + "/api/3/action" "/datastore_search_sql"


class FinancialYear(models.Model):
    organisational_unit = "financial_year"
    slug = models.SlugField(max_length=7, unique=True)
    published = models.BooleanField(default=False)
    _consolidated_expenditure_budget_dataset = None

    class Meta:
        ordering = ["-slug"]

    @property
    def national(self):
        return self.spheres.filter(slug=NATIONAL_SLUG)[0]

    @property
    def provincial(self):
        return self.spheres.filter(slug=PROVINCIAL_SLUG)[0]

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
    slug = AutoSlugField(
        populate_from="name",
        max_length=200,
        always_update=True,
    )
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
        if self.sphere.slug == NATIONAL_SLUG:
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


class DepartmentManager(models.Manager):
    def get_by_natural_key(
        self, financial_year, sphere_slug, government_slug, department_slug
    ):
        return self.get(
            slug=department_slug,
            government__slug=government_slug,
            government__sphere__slug=sphere_slug,
            government__sphere__financial_year__slug=financial_year,
        )


class Department(models.Model):
    objects = DepartmentManager()

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
        if self.government.sphere.slug == PROVINCIAL_SLUG:
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
        """Always return the latest available non-null URL, even for old departments."""
        newer_departments = Department.objects.filter(
            government__slug=self.government.slug,
            government__sphere__slug=self.government.sphere.slug,
            slug=self.slug,
            website_url__isnull=False,
        ).order_by("-government__sphere__financial_year__slug")
        return newer_departments.first().website_url if newer_departments else None

    def get_url_path(self):
        """e.g. 2018-19/national/departments/military-veterans"""
        return "%s/departments/%s" % (self.government.get_url_path(), self.slug)

    def get_preview_url_path(self):
        """e.g. 2018-19/previews/national/south-africa/agriculture-and-fisheries"""
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
        """Try to find the department in the most recent year with the same slug.
        Continue traversing backwards in time until found, or until the original year has been reached.
        """
        newer_departments = Department.objects.filter(
            government__slug=self.government.slug,
            government__sphere__slug=self.government.sphere.slug,
            slug=self.slug,
        ).order_by("-government__sphere__financial_year__slug")
        return newer_departments.first() if newer_departments else None

    def _get_financial_year_query(self):
        return '+vocab_financial_years:"%s"' % self.get_financial_year().slug

    def _get_government_query(self):
        if self.government.sphere.slug == PROVINCIAL_SLUG:
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
            self._estimates_of_econ_classes_expenditure_dataset[level] = (
                Dataset.from_package(package)
            )
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
        if self.government.sphere.slug == PROVINCIAL_SLUG:
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
        """Returns the total for each year:phase combination from the expenditure time series dataset."""
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
        """Returns a data object for each department, year and phase. Adds additional data required for the Treemap.
        From the Expenditure Time Series dataset."""
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
            government__sphere__slug=NATIONAL_SLUG, is_vote_primary=True
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
        """Returns a list of department objects nested in provinces."""
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
            government__sphere__slug=PROVINCIAL_SLUG,
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

        expenditure = {
            "nominal": [],
            "real": [],
        }

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

            expenditure.update(
                {
                    "base_financial_year": FinancialYear.slug_from_year_start(
                        str(base_year)
                    ),
                    "in_year_spending_enabled": config.IN_YEAR_SPENDING_ENABLED,
                    "department_name": self.name,
                }
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
    print(aggregate_url)
    querystring = "?api_url=" + quote(aggregate_url)
    csv_url = reverse("openspending_csv") + querystring
    if len(csv_url) > URL_LENGTH_LIMIT:
        raise Exception(
            "Generated URL exceeds max length of %s. "
            "Some browsers may no longer be able to interpret the URL."
            % URL_LENGTH_LIMIT
        )
    return csv_url


class PublicEntityManager(models.Manager):
    def get_by_natural_key(
        self, financial_year, sphere_slug, government_slug, public_entity_slug
    ):
        return self.get(
            slug=public_entity_slug,
            government__slug=government_slug,
            government__sphere__slug=sphere_slug,
            government__sphere__financial_year__slug=financial_year,
        )


class PublicEntity(models.Model):
    objects = PublicEntityManager()

    organisational_unit = "public_entity"
    government = models.ForeignKey(
        Government, on_delete=models.CASCADE, related_name="public_entities"
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=200,
        help_text="The public entity name must precisely match the text used "
        ". All datasets must be normalised to match this name. Beware that changing "
        "this name might cause a mismatch with already-published datasets which might "
        "need to be update to match this.",
    )
    slug = AutoSlugField(
        populate_from="name", max_length=200, always_update=True, editable=True
    )
    intro = models.TextField(default="", blank=True)

    pfma = models.CharField(
        max_length=10, blank=False, null=False, choices=PFMA_CHOICES
    )
    functiongroup1 = models.CharField(
        max_length=200, blank=True, null=True, choices=FUNCTIONGROUP1_CHOICES
    )

    amount = models.DecimalField(max_digits=20, decimal_places=0, default=0)

    class Meta:
        unique_together = (("government", "slug"), ("government", "name"))
        ordering = ["name"]
        verbose_name_plural = "public entities"

    @classmethod
    def get_in_latest_government(cls, name, government_name):
        """
        Get a public entity instance whose slug matches the provided name slugified,
        in the government with the provided name in the latest financial year.
        Returns None if a matching public entity is not found.
        """
        try:
            return cls.objects.filter(
                slug=slugify(name), government__name=government_name
            ).order_by("-government__sphere__financial_year__slug")[0]
        except IndexError:
            return None

    def get_url_path(self):
        """e.g. 2018-19/national/public-entities/military-veterans"""
        return "%s/public-entities/%s" % (self.government.get_url_path(), self.slug)

    def get_financial_year(self):
        return self.government.sphere.financial_year

    def get_latest_department_instance(self):
        """Try to find the department in the most recent year with the same slug.
        Continue traversing backwards in time until found, or until the original year has been reached.
        """
        newer_public_entities = PublicEntity.objects.filter(
            government__slug=self.government.slug,
            government__sphere__slug=self.government.sphere.slug,
            slug=self.slug,
        ).order_by("-government__sphere__financial_year__slug")
        return newer_public_entities.first() if newer_public_entities else None

    def _get_financial_year_query(self):
        return '+vocab_financial_years:"%s"' % self.get_financial_year().slug

    def _get_government_query(self):
        return none_selected_query("vocab_provinces")

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, self.get_url_path())


class PublicEntityExpenditure(models.Model):
    public_entity = models.ForeignKey(PublicEntity, on_delete=models.CASCADE)

    functiongroup2 = models.CharField(
        max_length=200, blank=True, null=True, choices=FUNCTIONGROUP1_CHOICES
    )

    expenditure_type = models.CharField(max_length=200, blank=True, null=True)

    consol_indi = models.CharField(max_length=10, blank=True, null=True)

    economic_classification1 = models.CharField(max_length=200, blank=True, null=True)
    economic_classification2 = models.CharField(max_length=200, blank=True, null=True)
    economic_classification3 = models.CharField(max_length=200, blank=True, null=True)
    economic_classification4 = models.CharField(max_length=200, blank=True, null=True)
    economic_classification5 = models.CharField(max_length=200, blank=True, null=True)
    economic_classification6 = models.CharField(max_length=200, blank=True, null=True)
    budget_phase = models.CharField(max_length=200, blank=True, null=True)

    amount = models.DecimalField(max_digits=20, decimal_places=0)
