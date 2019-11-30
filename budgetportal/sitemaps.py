from budgetportal.summaries import get_consolidated_expenditure_treemap
from django.contrib import sitemaps
from django.urls import reverse
from guide_data import category_guides

from .models import Department, FinancialYear, InfrastructureProjectPart


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


class InfrastructureProjectPartViewSitemap(sitemaps.Sitemap):
    def items(self):
        return InfrastructureProjectPart.objects.all()


class FocusViewSitemap(sitemaps.Sitemap):
    def items(self):
        focus_area_page_params = []
        for year in FinancialYear.get_available_years():
            treemap = get_consolidated_expenditure_treemap(year)
            for data in treemap["data"]["items"]:
                focus_area_page_params.append(
                    {"year": str(year.slug), "focus": data["id"]}
                )
        return focus_area_page_params

    def location(self, item):
        return reverse("focus", args=[item["year"], item["focus"]])


class GuidesViewSitemap(sitemaps.Sitemap):
    def items(self):
        return category_guides.values()

    def location(self, item):
        return reverse("guide-list", args=[item])


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
    "provincial_departments": ProvincialDepartmentsSitemap,
    "national_departments": NationalDepartmentsSitemap,
    "department_preview": DepartmentPreviewSitemap,
    "infrastructure_projects": InfrastructureProjectPartViewSitemap,
    "focus": FocusViewSitemap,
    "guides": GuidesViewSitemap,
    "search_results": SearchResultViewSitemap,
}
