from django.contrib import sitemaps
from django.urls import reverse
from budgetportal.summaries import get_consolidated_expenditure_treemap
from budgetportal.views import department_list_data
from guide_data import category_guides
from .models import InfrastructureProjectPart, FinancialYear


class ConsolidatedJsonViewSitemap(sitemaps.Sitemap):
    def items(self):
        years = []
        for year in FinancialYear.get_available_years():
            years.append(str(year.slug))

        return years

    def location(self, item):
        return reverse('consolidated', args=[item])


class DepartmentListViewSitemap(sitemaps.Sitemap):
    def items(self):
        years = []
        for year in FinancialYear.get_available_years():
            years.append(str(year.slug))

        return years

    def location(self, item):
        return reverse('department-list', args=[item])


class InfrastructureProjectPartViewSitemap(sitemaps.Sitemap):
    def items(self):
        return InfrastructureProjectPart.objects.all()


class FirstNationalDepartmentPreviewSitemap(sitemaps.Sitemap):
    def items(self):
        departments = department_list_data(financial_year_id='2016-17')
        department_slugs_2016_17 = []
        for department in departments["national"]:
            for data in department["departments"]:
                department_slugs_2016_17.append(data["slug"])
        return department_slugs_2016_17

    def location(self, item):
        return reverse(
            'department-preview',
            kwargs={
                'financial_year_id': '2016-17',
                'sphere_slug': 'national',
                'government_slug': 'south-africa',
                'department_slug': item
            }
        )


class SecondNationalDepartmentPreviewSitemap(sitemaps.Sitemap):
    def items(self):
        departments = department_list_data(financial_year_id='2017-18')
        department_slugs_2017_18 = []
        for department in departments["national"]:
            for data in department["departments"]:
                department_slugs_2017_18.append(data["slug"])
        return department_slugs_2017_18

    def location(self, item):
        return reverse(
            'department-preview',
            kwargs={
                'financial_year_id': '2017-18',
                'sphere_slug': 'national',
                'government_slug': 'south-africa',
                'department_slug': item
            }
        )


class ThirdNationalDepartmentPreviewSitemap(sitemaps.Sitemap):
    def items(self):
        departments = department_list_data(financial_year_id='2018-19')
        department_slugs_2018_19 = []
        for department in departments["national"]:
            for data in department["departments"]:
                department_slugs_2018_19.append(data["slug"])
        return department_slugs_2018_19

    def location(self, item):
        return reverse(
            'department-preview',
            kwargs={
                'financial_year_id': '2018-19',
                'sphere_slug': 'national',
                'government_slug': 'south-africa',
                'department_slug': item
            }
        )


class FourthNationalDepartmentPreviewSitemap(sitemaps.Sitemap):
    def items(self):
        departments = department_list_data(financial_year_id='2019-20')
        department_slugs_2019_20 = []
        for department in departments["national"]:
            for data in department["departments"]:
                department_slugs_2019_20.append(data["slug"])
        return department_slugs_2019_20

    def location(self, item):
        return reverse(
            'department-preview',
            kwargs={
                'financial_year_id': '2019-20',
                'sphere_slug': 'national',
                'government_slug': 'south-africa',
                'department_slug': item
            }
        )


class FirstFocusViewSitemap(sitemaps.Sitemap):
    def items(self):
        financial_year = FinancialYear.objects.get(slug='2016-17')
        treemap = get_consolidated_expenditure_treemap(financial_year)
        focus_slugs_2016_17 = []
        for data in treemap["data"]["items"]:
            focus_slugs_2016_17.append(data["id"])
        return focus_slugs_2016_17

    def location(self, item):
        return reverse(
            'focus',
            kwargs={
                'financial_year_id': '2016-17',
                'focus_slug': item,
            }
        )


class SecondFocusViewSitemap(sitemaps.Sitemap):
    def items(self):
        financial_year = FinancialYear.objects.get(slug='2017-18')
        treemap = get_consolidated_expenditure_treemap(financial_year)
        focus_slugs_2017_18 = []
        for data in treemap["data"]["items"]:
            focus_slugs_2017_18.append(data["id"])
        return focus_slugs_2017_18

    def location(self, item):
        return reverse(
            'focus',
            kwargs={
                'financial_year_id': '2017-18',
                'focus_slug': item,
            }
        )


class ThirdFocusViewSitemap(sitemaps.Sitemap):
    def items(self):
        financial_year = FinancialYear.objects.get(slug='2018-19')
        treemap = get_consolidated_expenditure_treemap(financial_year)
        focus_slugs_2018_19 = []
        for data in treemap["data"]["items"]:
            focus_slugs_2018_19.append(data["id"])
        return focus_slugs_2018_19

    def location(self, item):
        return reverse(
            'focus',
            kwargs={
                'financial_year_id': '2018-19',
                'focus_slug': item,
            }
        )


class FourthFocusViewSitemap(sitemaps.Sitemap):
    def items(self):
        financial_year = FinancialYear.objects.get(slug='2019-20')
        treemap = get_consolidated_expenditure_treemap(financial_year)
        focus_slugs_2019_20 = []
        for data in treemap["data"]["items"]:
            focus_slugs_2019_20.append(data["id"])
        return focus_slugs_2019_20

    def location(self, item):
        return reverse(
            'focus',
            kwargs={
                'financial_year_id': '2019-20',
                'focus_slug': item,
            }
        )


class FocusJsonViewSitemap(sitemaps.Sitemap):
    def items(self):
        years = []
        for year in FinancialYear.get_available_years():
            years.append(str(year.slug))

        return years

    def location(self, item):
        return reverse('focus-json', args=[item])


class GuidesViewSitemap(sitemaps.Sitemap):
    def items(self):
        return category_guides.values()

    def location(self, item):
        return reverse('guide', args=[item])


class SearchResultViewSitemap(sitemaps.Sitemap):
    def items(self):
        years = []
        for year in FinancialYear.get_available_years():
            years.append(str(year.slug))

        return years

    def location(self, item):
        return reverse('search-result', args=[item])


class StaticViewSitemap(sitemaps.Sitemap):
    def items(self):
        return ['home', 'about', 'events', 'videos', 'terms-and-conditions',
                'resources', 'glossary', 'faq', 'dataset-landing-page',
                'guides', 'infrastructure-project-list']

    def location(self, item):
        return reverse(item)


sitemaps = {
    'static': StaticViewSitemap,
    'consolidated': ConsolidatedJsonViewSitemap,
    'departments': DepartmentListViewSitemap,
    'nationa_department_preview_2016_17': FirstNationalDepartmentPreviewSitemap,
    'national_department_preview_2017_18': SecondNationalDepartmentPreviewSitemap,
    'national_department_preview_2018_19': ThirdNationalDepartmentPreviewSitemap,
    'national_department_preview_2019_20': FourthNationalDepartmentPreviewSitemap,
    'infrastructure_projects': InfrastructureProjectPartViewSitemap,
    'focus_2016_17': FirstFocusViewSitemap,
    'focus_2017_18': SecondFocusViewSitemap,
    'focus_2018_19': ThirdFocusViewSitemap,
    'focus_2019_20': FourthFocusViewSitemap,
    'focus_json': FocusJsonViewSitemap,
    'guides': GuidesViewSitemap,
    'search_results': SearchResultViewSitemap,
}
