from django.contrib import sitemaps
from django.urls import reverse
from budgetportal.summaries import get_focus_area_preview
from guide_data import category_guides
from .models import InfrastructureProjectPart, FinancialYear


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


class DepartmentPreviewViewSitemap(sitemaps.Sitemap):
    def items(self):
        financial_year = FinancialYear.objects.get(slug='2016-17')
        focus_preview_2016_17 = get_focus_area_preview(financial_year)
        department_slugs_2016_17 = []
        for item in focus_preview_2016_17['data']['items']:
            for data in item["national"]["data"]:
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
    'departments': DepartmentListViewSitemap,
    'department_preview': DepartmentPreviewViewSitemap,
    'infrastructure_projects': InfrastructureProjectPartViewSitemap,
    'focus_json': FocusJsonViewSitemap,
    'guides': GuidesViewSitemap,
    'search_results': SearchResultViewSitemap,
}