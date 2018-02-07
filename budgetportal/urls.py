from django.conf.urls import url
from django.views.decorators.cache import cache_page
from django.contrib import admin
from adminplus.sites import AdminSitePlus

from . import views

admin.site = AdminSitePlus()
admin.autodiscover()

CACHE_SECS = 0


urlpatterns = [

    # Home Page revenue
    url(r'^(?P<financial_year_id>[\w-]+).yaml$',
        cache_page(CACHE_SECS)(views.home)),


    # Basic pages
    url(r'^(?P<financial_year_id>[\w-]+).yaml',
        cache_page(CACHE_SECS)(views.Page.as_view(
            slug='index',
            organisational_unit='financial_year',
        ))),
    url(r'^index.yaml',
        cache_page(CACHE_SECS)(views.Page.as_view(
            slug='index',
            organisational_unit='financial_year',
        ))),

    url(r'^(?P<financial_year_id>[\w-]+)/about.yaml',
        cache_page(CACHE_SECS)(views.Page.as_view(
            slug='about',
            organisational_unit='about',
        ))),
    url(r'^(?P<financial_year_id>[\w-]+)/glossary.yaml',
        cache_page(CACHE_SECS)(views.Page.as_view(
            slug='glossary',
            organisational_unit='learning',
        ))),
    url(r'^(?P<financial_year_id>[\w-]+)/resources.yaml',
        cache_page(CACHE_SECS)(views.Page.as_view(
            slug='resources',
            organisational_unit='learning',
        ))),
    url(r'^(?P<financial_year_id>[\w-]+)/search-result.yaml',
        cache_page(CACHE_SECS)(views.Page.as_view(
            slug='search-result',
            organisational_unit='financial_year',
        ))),
    url(r'^(?P<financial_year_id>[\w-]+)/videos.yaml',
        cache_page(CACHE_SECS)(views.Page.as_view(
            slug='videos',
            organisational_unit='learning',
        ))),


    # Department List
    url(r'^(?P<financial_year_id>[\w-]+)'
        '/departments.yaml', cache_page(CACHE_SECS)(views.department_list)),

    # Department
    url(r'^(?P<financial_year_id>[\w-]+)'
        '/national'
        '/departments'
        '/(?P<department_slug>[\w-]+).yaml$', cache_page(CACHE_SECS)(views.department),
        kwargs={'sphere_slug': 'national', 'government_slug': 'south-africa'}),
    url(r'^(?P<financial_year_id>[\w-]+)'
        '/(?P<sphere_slug>[\w-]+)'
        '/(?P<government_slug>[\w-]+)'
        '/departments'
        '/(?P<department_slug>[\w-]+).yaml$', cache_page(CACHE_SECS)(views.department)),


    # Contributed Dataset List
    url(r'^(?P<financial_year_id>[\w-]+)'
        '/contributed-data.yaml', cache_page(CACHE_SECS)(views.contributed_dataset_list)),


    # Dataset
    url(r'^(?P<financial_year_id>[\w-]+)'
        '/datasets'
        '/(?P<dataset_slug>[\w-]+).yaml$', cache_page(CACHE_SECS)(views.dataset)),


    # Admin
    url(r'^admin/', admin.site.urls),
]
