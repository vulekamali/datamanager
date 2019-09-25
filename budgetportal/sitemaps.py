from django.contrib import sitemaps
from django.contrib.sitemaps import GenericSitemap
from django.urls import reverse

from .models import InfrastructureProjectPart, FinancialYear
from guide_data import category_guides


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


class FocusViewSitemap(sitemaps.Sitemap):
    def items(self):
        years = []
        for year in FinancialYear.get_available_years():
            years.append(str(year.slug))

        return years

    def location(self, item):
        # TODO: not working yet
        return reverse('focus', kwargs={'financial_year_id':  item, 'focus_slug': 'health'})


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
    'infrastructure_projects': InfrastructureProjectPartViewSitemap,
    'focus': FocusViewSitemap,
    'focus_json': FocusJsonViewSitemap,
    'guides': GuidesViewSitemap,
    'search_results': SearchResultViewSitemap,
}