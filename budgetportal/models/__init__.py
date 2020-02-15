import logging
import uuid
from datetime import datetime
from pprint import pformat

import requests
from slugify import slugify

from adminsortable.models import SortableMixin
from budgetportal.datasets import Dataset
from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.urls import reverse

from .gov_structure import (
    Department,
    FinancialYear,
    Government,
    GovtFunction,
    Programme,
    Sphere,
)

logger = logging.getLogger(__name__)
ckan = settings.CKAN

CKAN_DATASTORE_URL = settings.CKAN_URL + "/api/3/action" "/datastore_search_sql"

MAPIT_POINT_API_URL = "https://mapit.code4sa.org/point/4326/{},{}"

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


class InfrastructureProjectPart(models.Model):
    sphere = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
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
    amount = models.BigIntegerField(default=0)
    financial_year = models.CharField(max_length=4)
    total_project_cost = models.BigIntegerField(default=0)
    provinces = models.CharField(max_length=510, default="")
    gps_code = models.CharField(max_length=255, default="")

    class Meta:
        verbose_name = "National infrastructure project part"

    def __str__(self):
        return "{} ({} {})".format(
            self.project_slug, self.budget_phase, self.financial_year
        )

    def get_budget_document_url(self, document_format="PDF"):
        """
        Returns budget-vote-document URL, for given format,
        if the latest department instance matches the project year
        """
        departments = Department.objects.filter(
            slug=slugify(self.department), government__sphere__slug="national"
        )
        if departments:
            latest_dept = departments[0].get_latest_department_instance()
            project_year = self.get_dataset().package["financial_year"][0]
            if latest_dept.get_financial_year().slug == project_year:
                budget_dataset = latest_dept.get_dataset(
                    group_name="budget-vote-documents"
                )
                if budget_dataset:
                    document_resource = budget_dataset.get_resource(
                        format=document_format
                    )
                    if document_resource:
                        return document_resource["url"]
        return None

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
            projected_expenditure += float(project.amount)
        return projected_expenditure

    @staticmethod
    def _parse_coordinate(coordinate):
        """ Expects a single set of coordinates (lat, long) split by a comma """
        if not isinstance(coordinate, (str, unicode)):
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
        params = {"type": "PR"}
        province_result = requests.get(
            MAPIT_POINT_API_URL.format(coordinate["longitude"], coordinate["latitude"]),
            params=params,
        )
        province_result.raise_for_status()
        r = province_result.json()
        list_of_objects_returned = r.values()
        if len(list_of_objects_returned) > 0:
            province_name = list_of_objects_returned[0]["name"]
            return province_name
        else:
            return None

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
            "amount": project.amount,
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

    @classmethod
    def get_dataset(cls):
        """ Return the first dataset in the Infrastructure Projects group. """
        query = {
            "q": "",
            "fq": (
                '+organization:"national-treasury"'
                '+vocab_spheres:"national"'
                '+groups:"infrastructure-projects"'
            ),
            "rows": 1,
        }
        response = ckan.action.package_search(**query)
        logger.info(
            "query %s\nreturned %d results", pformat(query), len(response["results"])
        )
        if response["results"]:
            return Dataset.from_package(response["results"][0])
        else:
            return None


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
    video = models.ForeignKey("Video", null=True, blank=True)
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

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ["the_order"]


class Quarter(models.Model):
    number = models.IntegerField(unique=True)

    class Meta:
        ordering = ["number"]

    def __unicode__(self):
        return u"Quarter %d" % self.number


def irm_snapshot_file_path(instance, filename):
    extension = filename.split(".")[-1]
    return "irm-snapshots/%s/%s-Q%d-taken-%s.%s" % (
        uuid.uuid4(),
        instance.financial_year.slug,
        instance.quarter.number,
        instance.date_taken.isoformat()[:18],
        extension,
    )


class IRMSnapshot(models.Model):
    """This represents a particular snapshot from IRM"""

    financial_year = models.ForeignKey(FinancialYear, on_delete=models.CASCADE)
    quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE)
    date_taken = models.DateTimeField()
    file = models.FileField(upload_to=irm_snapshot_file_path)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        ordering = ["financial_year__slug", "quarter__number"]
        verbose_name = "IRM Snapshot"
        unique_together = ["financial_year", "quarter"]

    def __unicode__(self):
        return u"%s Q%d taken %s" % (
            self.financial_year.slug,
            self.quarter.number,
            self.date_taken.isoformat()[:18],
        )


class ProvInfraProject(models.Model):
    """This represents a project, grouping its snapshots"""

    IRM_project_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = "Provincial infrastructure project"

    def __unicode__(self):
        if self.project_snapshots.count():
            return self.project_snapshots.latest().name
        else:
            return u"IRM project ID %d (no snapshots loaded)" % self.IRM_project_id

    def get_slug(self):
        return slugify(
            u"{0} {1}".format(
                self.project_snapshots.latest().name,
                self.project_snapshots.latest().province,
            )
        )

    def get_absolute_url(self):
        args = [self.pk, self.get_slug()]
        return reverse("provincial-infra-project-detail", args=args)


class ProvInfraProjectSnapshot(models.Model):
    """This represents a snapshot of a project, as it occurred in an IRM snapshot"""

    irm_snapshot = models.ForeignKey(
        IRMSnapshot, on_delete=models.CASCADE, related_name="project_snapshots"
    )
    project = models.ForeignKey(
        ProvInfraProject, on_delete=models.CASCADE, related_name="project_snapshots"
    )
    project_number = models.CharField(max_length=1024, blank=True, null=True)
    name = models.CharField(max_length=1024, blank=True, null=True)
    province = models.CharField(max_length=1024, blank=True, null=True)
    department = models.CharField(max_length=1024, blank=True, null=True)
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
    total_project_cost = models.DecimalField(
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
    adjustment_appropriation_professional_fees = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    main_appropriation_construction_costs = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    adjustment_appropriation_construction_costs = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    main_appropriation_total = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    adjustment_appropriation_total = models.DecimalField(
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
            "irm_snapshot__financial_year__slug",
            "irm_snapshot__quarter__number",
        ]
        get_latest_by = "irm_snapshot"
        verbose_name = "Provincial infrastructure project snapshot"
        unique_together = ["irm_snapshot", "project"]

    def __unicode__(self):
        return self.name
