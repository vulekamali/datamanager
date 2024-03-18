import logging
import re
import uuid
from collections import OrderedDict
from datetime import datetime

import requests
from slugify import slugify

import ckeditor.fields as ckeditor_fields
from adminsortable.models import SortableMixin
from budgetportal.blocks import DescriptionEmbedBlock, SectionBlock
from budgetportal.datasets import Dataset
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core import blocks as wagtail_blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet

from .government import (
    FinancialYear,
    Sphere,
    Government,
    GovtFunction,
    Department,
    PublicEntity,
    Programme,
    SPHERE_SLUG_CHOICES,
    NATIONAL_SLUG,
    PROVINCIAL_SLUG,
    EXPENDITURE_TIME_SERIES_PHASE_MAPPING,
)

logger = logging.getLogger(__name__)
ckan = settings.CKAN

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
        """Calculate sum of predicted amounts from a list of records"""
        projected_records_for_project = InfrastructureProjectPart.objects.filter(
            budget_phase="MTEF", project_slug=self.project_slug
        )
        projected_expenditure = 0
        for project in projected_records_for_project:
            projected_expenditure += float(project.amount_rands or 0.0)
        return projected_expenditure

    @staticmethod
    def _parse_coordinate(coordinate):
        """Expects a single set of coordinates (lat, long) split by a comma"""
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
        """Expects a cleaned coordinate"""
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
        """Searches name of project for province name or abbreviation"""
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
        """Returns a list of provinces based on values in self.coordinates"""
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
    content = ckeditor_fields.RichTextField()
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
    """
    This represents a project, grouping its snapshots by project's ID in IRM.
    This assumes the same project will have the same ID in IRM across financial years.

    The internal ID of these instances is used as the ID in the URL, since we don't
    want to expose IRM IDs publicly but we want to have a consistent URL for projects.

    We don't delete these even when there's no snapshots associated with them
    so that the URL based on this id remains consistent in case projects with this
    IRM ID are uploaded after snapshots are deleted.
    """

    IRM_project_id = models.IntegerField()
    sphere_slug = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = "Infrastructure project"
        unique_together = ["sphere_slug", "IRM_project_id"]

    def __str__(self):
        if self.project_snapshots.count():
            return self.project_snapshots.latest().name
        else:
            return f"{self.sphere_slug} IRM project ID {self.IRM_project_id} (no snapshots loaded)"

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
        if self.irm_snapshot.sphere.slug == NATIONAL_SLUG:
            return "South Africa"
        elif self.irm_snapshot.sphere.slug == PROVINCIAL_SLUG:
            return self.province
        else:
            raise Exception(f"Unexpected sphere {self.irm_snapshot.sphere}")

    @property
    def government_label(self):
        if self.irm_snapshot.sphere.slug == NATIONAL_SLUG:
            return "National"
        elif self.irm_snapshot.sphere.slug == PROVINCIAL_SLUG:
            return self.province
        else:
            raise Exception(f"Unexpected sphere {self.irm_snapshot.sphere}")

    @property
    def financial_year(self):
        return self.irm_snapshot.sphere.financial_year.slug

    def __str__(self):
        return self.name


class NavContextMixin:
    def get_context(self, request):
        context = super().get_context(request)
        nav = MainMenuItem.objects.prefetch_related("children").all()

        context["navbar"] = nav

        for item in nav:
            if item.name and item.url and request.path.startswith(item.url):
                context["selected_tab"] = item.name

        return context


class WagtailHomePage(NavContextMixin, Page):
    max_count = 1


class CustomPage(NavContextMixin, Page):
    body = StreamField(
        [
            ("section", SectionBlock()),
            ("html", wagtail_blocks.RawHTMLBlock()),
            ("chart_embed", DescriptionEmbedBlock()),
        ]
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
    ]


class LearningIndexPage(NavContextMixin, Page):
    parent_page_types = ["budgetportal.WagtailHomePage"]
    subpage_types = ["budgetportal.GuideIndexPage"]
    max_count = 1


class PostIndexPage(NavContextMixin, Page):
    parent_page_types = ["budgetportal.WagtailHomePage"]
    subpage_types = ["budgetportal.PostPage"]
    max_count = 1
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro", classname="full")]


class GuideIndexPage(NavContextMixin, Page):
    max_count = 1
    parent_page_types = ["budgetportal.LearningIndexPage"]
    subpage_types = ["budgetportal.GuidePage"]
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro", classname="full")]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        guides = {p.title: p for p in self.get_children().live()}
        for external in CategoryGuide.objects.filter(external_url__isnull=False):
            guides[external.external_url_title] = external

        context["guides"] = OrderedDict(sorted(guides.items())).values()
        return context


class GuidePage(NavContextMixin, Page):
    parent_page_types = ["budgetportal.GuideIndexPage"]
    body = StreamField(
        [
            ("section", SectionBlock()),
            ("html", wagtail_blocks.RawHTMLBlock()),
            ("chart_embed", DescriptionEmbedBlock()),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
        ImageChooserPanel("image"),
    ]


class CategoryGuide(models.Model):
    """Link GuidePages or external URLs to dataset category slugs"""

    category_slug = models.SlugField(max_length=200, unique=True)
    guide_page = models.ForeignKey(
        GuidePage, null=True, blank=True, on_delete=models.CASCADE
    )
    external_url = models.URLField(null=True, blank=True)
    external_url_title = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text=(
            "Only shown if External URL is used. This may be truncated so "
            "use a short description that will also be seen on the external page."
        ),
    )
    external_url_description = models.TextField(
        null=True,
        blank=True,
        help_text=(
            "Only shown if External URL is used. This may be truncated so "
            "use a short description that will also be seen on the external page."
        ),
    )

    def __str__(self):
        return "{} - {}".format(
            self.category_slug, self.guide_page or self.external_url
        )

    def clean(self):
        if self.external_url is None and self.guide_page is None:
            raise ValidationError("Either Guide Page or External URL must be set.")
        if self.external_url is not None and self.guide_page is not None:
            raise ValidationError("Only one of Guide Page or External URL may be set.")
        if self.external_url is not None and self.external_url_title is None:
            raise ValidationError("Title is required when using External URL.")

        return super().clean()


class PostPage(NavContextMixin, Page):
    parent_page_types = ["budgetportal.PostIndexPage"]
    body = StreamField(
        [
            ("section", SectionBlock()),
            ("html", wagtail_blocks.RawHTMLBlock()),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
    ]


class MainMenuItem(SortableMixin):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    url = models.CharField(
        max_length=1000,
        help_text="Use URLs relative to the site root (e.g. /about) for urls on this site.",
        blank=True,
        null=True,
    )
    align_right = models.BooleanField()
    main_menu_item_order = models.PositiveIntegerField(
        default=0, editable=False, db_index=True
    )
    highlight_as_new = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["main_menu_item_order"]

    def __str__(self):
        return f"{self.label} ({self.url}) ({self.children.count()} children)"


class SubMenuItem(SortableMixin):
    parent = models.ForeignKey(
        MainMenuItem, on_delete=models.CASCADE, related_name="children"
    )
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    url = models.CharField(
        max_length=1000,
        help_text="Use URLs relative to the site root (e.g. /about) for urls on this site.",
    )
    sub_menu_item_order = models.PositiveIntegerField(
        default=0, editable=False, db_index=True
    )

    class Meta:
        ordering = ["sub_menu_item_order"]

    def __str__(self):
        return f"{self.parent.label} > {self.label} ({self.url})"


class Notice(SortableMixin):
    """
    Any number of notices shown at the top of the site. Intended e.g. to configure
    the staging site to make it clear to users that that instance is not necessarily
    correct, but for testing only.
    """

    description = models.CharField(max_length=1024)
    content = ckeditor_fields.RichTextField()

    notice_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        ordering = ["notice_order"]

    def __str__(self):
        return self.description


class ResourceLink(models.Model):
    title = models.CharField(max_length=150)
    url = models.URLField(null=True, blank=True)
    description = models.CharField(max_length=300)
    resource_link_order = models.PositiveIntegerField(
        default=0, db_index=True, help_text="Links are shown in this order."
    )
    sphere_slug = models.CharField(
        max_length=100,
        choices=[
            ("all", "All"),
        ]
        + SPHERE_SLUG_CHOICES,
        default="all",
        verbose_name="Sphere",
        help_text="Only show on pages for this sphere or all spheres.",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("url"),
                FieldPanel("description"),
            ],
            heading="Content",
        ),
        MultiFieldPanel(
            [
                FieldPanel("resource_link_order"),
                FieldPanel("sphere_slug"),
            ],
            heading="Display options",
        ),
    ]

    def __str__(self):
        return self.title

    class Meta:
        abstract = True
        ordering = ["resource_link_order"]


def showcase_item_file_path(instance, filename):
    extension = filename.split(".")[-1]
    return f"showcase-items/{uuid.uuid4()}.{extension}"


class ShowcaseItem(SortableMixin):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
    cta_text_1 = models.CharField(max_length=200, verbose_name="Call to action text 1")
    cta_link_1 = models.URLField(
        null=True, blank=True, verbose_name="Call to action link 1"
    )
    cta_text_2 = models.CharField(
        max_length=200, verbose_name="Call to action text 2", null=True, blank=True
    )
    cta_link_2 = models.URLField(
        null=True, blank=True, verbose_name="Call to action link 2"
    )
    second_cta_type = models.CharField(
        max_length=255,
        choices=(("primary", "Primary"), ("secondary", "Secondary")),
        verbose_name="Second call to action type",
    )
    file = models.FileField(
        upload_to=showcase_item_file_path,
        help_text=mark_safe(
            "<ul><li style='list-style:square'>Thumbnail aspect ratio should be 1.91:1.</li>"
            "<li style='list-style:square'>Recommended resolution is 1200 x 630 px.</li>"
            "<li style='list-style:square'>Main focus of image should be centered occupying 630 x 630 px in the middle of the image.</li></ul>"
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    item_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        ordering = ["item_order"]

    def __str__(self):
        return self.name


@register_snippet
class ProcurementResourceLink(ResourceLink):
    class Meta:
        verbose_name = "Procurement resource link"
        verbose_name_plural = "Procurement resource links"


@register_snippet
class PerformanceResourceLink(ResourceLink):
    class Meta:
        verbose_name = "Performance resource link"
        verbose_name_plural = "Performance resource links"


@register_snippet
class InYearMonitoringResourceLink(ResourceLink):
    class Meta:
        verbose_name = "In-year monitoring resource link"
        verbose_name_plural = "In-year monitoring resource links"
