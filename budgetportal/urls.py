from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page

from . import views

CACHE_SECS = 12 * 60 * 60

urlpatterns = patterns(
    '',
    url(r'^$', 'budgetportal.views.home', name='home'),

    # Department List
    url(r'^(?P<financial_year>[\w-]+)'
        '/departments.yaml', cache_page(CACHE_SECS)(views.department_list)),
)
