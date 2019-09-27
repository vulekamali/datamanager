from django.contrib import sitemaps
from django.urls import reverse
from budgetportal.summaries import get_consolidated_expenditure_treemap
from guide_data import category_guides
from .models import InfrastructureProjectPart, FinancialYear, Department, \
    EXPENDITURE_TIME_SERIES_PHASE_MAPPING, Government


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
        return Department.objects.filter(government__sphere__slug='provincial')

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
        return Department.objects.filter(government__sphere__slug='national')

    def location(self, item):
        return reverse(
            "national-department",
            args=[
                item.government.sphere.financial_year.slug,
                item.slug,
            ],
        )


class DepartmentPreviewSitemap(sitemaps.Sitemap):
    def items(self):
        return Department.objects.all()

    def location(self, item):
        print item
        return reverse(
            "department-preview",
            args=[
                item.government.sphere.financial_year.slug,
                item.government.sphere.slug,
                item.government.slug,
                item.slug,
            ],
        )


class FirstDepartmentPreviewJsonSitemap(sitemaps.Sitemap):
    def items(self):
        return Government.objects.all()

    def location(self, item):
        return reverse(
            "department-preview-json",
            args=[
                item.sphere.financial_year.slug,
                item.sphere.slug,
                item.slug,
                EXPENDITURE_TIME_SERIES_PHASE_MAPPING.keys()[0],
            ],
        )


class SecondDepartmentPreviewJsonSitemap(sitemaps.Sitemap):
    def items(self):
        return Government.objects.all()

    def location(self, item):
        return reverse(
            "department-preview-json",
            args=[
                item.sphere.financial_year.slug,
                item.sphere.slug,
                item.slug,
                EXPENDITURE_TIME_SERIES_PHASE_MAPPING.keys()[1],
            ],
        )


class ThirdDepartmentPreviewJsonSitemap(sitemaps.Sitemap):
    def items(self):
        return Government.objects.all()

    def location(self, item):
        return reverse(
            "department-preview-json",
            args=[
                item.sphere.financial_year.slug,
                item.sphere.slug,
                item.slug,
                EXPENDITURE_TIME_SERIES_PHASE_MAPPING.keys()[2],
            ],
        )


class InfrastructureProjectPartViewSitemap(sitemaps.Sitemap):
    def items(self):
        return InfrastructureProjectPart.objects.all()


class FirstFocusViewSitemap(sitemaps.Sitemap):
    def items(self):
        financial_year = FinancialYear.objects.get(slug="2016-17")
        treemap = get_consolidated_expenditure_treemap(financial_year)
        focus_slugs_2016_17 = []
        for data in treemap["data"]["items"]:
            focus_slugs_2016_17.append(data["id"])
        return focus_slugs_2016_17

    def location(self, item):
        return reverse(
            "focus", kwargs={"financial_year_id": "2016-17", "focus_slug": item}
        )


class SecondFocusViewSitemap(sitemaps.Sitemap):
    def items(self):
        financial_year = FinancialYear.objects.get(slug="2017-18")
        treemap = get_consolidated_expenditure_treemap(financial_year)
        focus_slugs_2017_18 = []
        for data in treemap["data"]["items"]:
            focus_slugs_2017_18.append(data["id"])
        return focus_slugs_2017_18

    def location(self, item):
        return reverse(
            "focus", kwargs={"financial_year_id": "2017-18", "focus_slug": item}
        )


class ThirdFocusViewSitemap(sitemaps.Sitemap):
    def items(self):
        financial_year = FinancialYear.objects.get(slug="2018-19")
        treemap = get_consolidated_expenditure_treemap(financial_year)
        focus_slugs_2018_19 = []
        for data in treemap["data"]["items"]:
            focus_slugs_2018_19.append(data["id"])
        return focus_slugs_2018_19

    def location(self, item):
        return reverse(
            "focus", kwargs={"financial_year_id": "2018-19", "focus_slug": item}
        )


class FourthFocusViewSitemap(sitemaps.Sitemap):
    def items(self):
        financial_year = FinancialYear.objects.get(slug="2019-20")
        treemap = get_consolidated_expenditure_treemap(financial_year)
        focus_slugs_2019_20 = []
        for data in treemap["data"]["items"]:
            focus_slugs_2019_20.append(data["id"])
        return focus_slugs_2019_20

    def location(self, item):
        return reverse(
            "focus", kwargs={"financial_year_id": "2019-20", "focus_slug": item}
        )


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
    "department_preview_json_1": FirstDepartmentPreviewJsonSitemap,
    "department_preview_json_2": SecondDepartmentPreviewJsonSitemap,
    "department_preview_json_3": ThirdDepartmentPreviewJsonSitemap,
    "infrastructure_projects": InfrastructureProjectPartViewSitemap,
    "focus_2016_17": FirstFocusViewSitemap,
    "focus_2017_18": SecondFocusViewSitemap,
    "focus_2018_19": ThirdFocusViewSitemap,
    "focus_2019_20": FourthFocusViewSitemap,
    "focus_json": FocusJsonViewSitemap,
    "guides": GuidesViewSitemap,
    "search_results": SearchResultViewSitemap,
}
