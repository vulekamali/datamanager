from django.contrib import sitemaps
from django.contrib.sitemaps import GenericSitemap
from django.urls import reverse

from .models import InfrastructureProjectPart, Department
from guide_data import category_guides

infrastructure_project_dict = {
    'queryset': InfrastructureProjectPart.objects.all()
}
infrastructure_project_sitemap = GenericSitemap(infrastructure_project_dict, priority=0.6)


class FocusViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        area = ('health', 'test', 'deneme')
        return area

    def years(self):
        years = ('2015-16', '2019-20',)
        return years

    def location(self, item):
        # TODO: not working yet
        # return reverse('focus', kwargs={'financial_year_id': '2019-20', 'focus_slug': 'health'})
        return reverse('focus', kwargs={'financial_year_id': self.years, 'focus_slug': item})


class GuidesViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return category_guides.values()

    def location(self, item):
        return reverse('guide', args=[item])


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['about', 'events', 'videos', 'terms-and-conditions', 'resources',
                'glossary', 'faq', 'dataset-landing-page']

    def location(self, item):
        return reverse(item)


sitemaps = {
    'static': StaticViewSitemap,
    'infrastructure_projects': infrastructure_project_sitemap,
    'focus': FocusViewSitemap,
    'guides': GuidesViewSitemap,
}