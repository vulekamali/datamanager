from django.contrib import sitemaps
from django.urls import reverse
from budgetportal.summaries import get_consolidated_expenditure_treemap
from guide_data import category_guides
from .models import (
    InfrastructureProjectPart,
    FinancialYear,
    Department,
    EXPENDITURE_TIME_SERIES_PHASE_MAPPING,
    Government,
)


class ConsolidatedJsonViewSitemap(sitemaps.Sitemap):
    def items(self):
        years = []
        for year in FinancialYear.get_available_years():
            years.append(str(year.slug))

        return years

    def location(self, item):
        return reverse("consolidated", args=[item])


class DepartmentListViewSitemap(sitemaps.Sitemap):
    def items(self):
        years = []
        for year in FinancialYear.get_available_years():
            years.append(str(year.slug))

        return years

    def location(self, item):
        return reverse("department-list", args=[item])


class ProvincialDepartmentsSitemap(sitemaps.Sitemap):
    def items(self):
        return Department.objects.filter(government__sphere__slug="provincial")

    def location(self, item):
        return reverse(
            "provincial-department",
            args=[
                item.government.sphere.financial_year.slug,
                item.government.sphere.slug,
                item.government.slug,
                item.slug,
            ],
        )


class NationalDepartmentsSitemap(sitemaps.Sitemap):
    def items(self):
        return Department.objects.filter(government__sphere__slug="national")

    def location(self, item):
        return reverse(
            "national-department",
            args=[item.government.sphere.financial_year.slug, item.slug],
        )


class DepartmentPreviewSitemap(sitemaps.Sitemap):
    def items(self):
        return Department.objects.all()

    def location(self, item):
        return reverse(
            "department-preview",
            args=[
                item.government.sphere.financial_year.slug,
                item.government.sphere.slug,
                item.government.slug,
                item.slug,
            ],
        )


class DepartmentPreviewJsonSitemap(sitemaps.Sitemap):
    def items(self):
        department_preview_json = []
        governments = Government.objects.all()
        for government in governments:
            for key in EXPENDITURE_TIME_SERIES_PHASE_MAPPING.keys():
                department_preview_json.append({"government": government, "phase": key})
        return department_preview_json

    def location(self, item):
        return reverse(
            "department-preview-json",
            args=[
                item["government"].sphere.financial_year.slug,
                item["government"].sphere.slug,
                item["government"].slug,
                item["phase"],
            ],
        )


class InfrastructureProjectPartViewSitemap(sitemaps.Sitemap):
    def items(self):
        return InfrastructureProjectPart.objects.all()


class FocusViewSitemap(sitemaps.Sitemap):
    def items(self):
        focus_slugs = []
        for year in FinancialYear.get_available_years():
            treemap = get_consolidated_expenditure_treemap(year)
            for data in treemap["data"]["items"]:
                focus_slugs.append({"year": str(year.slug), "focus": data["id"]})
        return focus_slugs

    def location(self, item):
        return reverse("focus", args=[item["year"], item["focus"]])


class FocusJsonViewSitemap(sitemaps.Sitemap):
    def items(self):
        years = []
        for year in FinancialYear.get_available_years():
            years.append(str(year.slug))

        return years

    def location(self, item):
        return reverse("focus-json", args=[item])


class GuidesViewSitemap(sitemaps.Sitemap):
    def items(self):
        return category_guides.values()

    def location(self, item):
        return reverse("guide", args=[item])


class SearchResultViewSitemap(sitemaps.Sitemap):
    def items(self):
        years = []
        for year in FinancialYear.get_available_years():
            years.append(str(year.slug))

        return years

    def location(self, item):
        return reverse("search-result", args=[item])


class StaticViewSitemap(sitemaps.Sitemap):
    def items(self):
        return [
            "home",
            "about",
            "events",
            "videos",
            "terms-and-conditions",
            "resources",
            "glossary",
            "faq",
            "dataset-landing-page",
            "guides",
            "infrastructure-project-list",
        ]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "static": StaticViewSitemap,
    "consolidated": ConsolidatedJsonViewSitemap,
    "provincial_departments": ProvincialDepartmentsSitemap,
    "national_departments": NationalDepartmentsSitemap,
    "department_preview": DepartmentPreviewSitemap,
    "department_preview_json": DepartmentPreviewJsonSitemap,
    "infrastructure_projects": InfrastructureProjectPartViewSitemap,
    "focus": FocusViewSitemap,
    "focus_json": FocusJsonViewSitemap,
    "guides": GuidesViewSitemap,
    "search_results": SearchResultViewSitemap,
}
