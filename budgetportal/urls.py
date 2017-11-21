from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page

from . import views

CACHE_SECS = 12 * 60 * 60

urlpatterns = patterns(
    '',
    url(r'^$', 'budgetportal.views.home', name='home'),

    url(r'^(?P<financial_year>[\w-]+)'
        '/national'
        '/departments'
        '/(?P<department_name_slug>[\w-]+)$', cache_page(CACHE_SECS)(views.department),
        kwargs={'sphere': 'national', 'geographic_region_slug': 'south-africa'}),
    url(r'^(?P<financial_year>[\w]+)'
        '/(?P<sphere>[\w]+)'
        '/(?P<geographic_region_slug>[\w_]+)'
        '/departments'
        '/(?P<department_slug>[\w_]+)$', cache_page(CACHE_SECS)(views.department)),
)
