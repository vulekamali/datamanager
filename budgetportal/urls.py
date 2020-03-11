from adminplus.sites import AdminSitePlus
from discourse.views import sso
from django.conf import settings
from django.conf.urls import include, url
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib import admin
from django.contrib.sitemaps import views as sitemap_views
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import cache_page
from .sitemaps import sitemaps
from .webflow import urls as webflow_urls

from . import bulk_upload, views

admin.site = AdminSitePlus()
admin.autodiscover()

CACHE_MINUTES_SECS = 60 * 5  # minutes
CACHE_DAYS_SECS = 60 * 60 * 24 * 5  # days


def permission_denied(request):
    raise PermissionDenied()


def trigger_error(request):
    division_by_zero = 1 / 0


department_urlpatterns = [
    url(
        r"^$", cache_page(CACHE_MINUTES_SECS)(views.department_page), name="department"
    ),
    url(
        r"^viz/subprog-treemap$",
        cache_page(CACHE_DAYS_SECS)(views.department_viz_subprog_treemap),
        name="department-viz-subprog-treemap",
    ),
    url(
        r"^viz/subprog-econ4-circles$",
        cache_page(CACHE_DAYS_SECS)(views.department_viz_subprog_econ4_circles),
        name="department-viz-subprog-econ4-circles",
    ),
    url(
        r"^viz/subprog-econ4-bars$",
        cache_page(CACHE_DAYS_SECS)(views.department_viz_subprog_econ4_bars),
        name="department-viz-subprog-econ4-bars",
    ),
]

urlpatterns = [
    url("sentry-debug/", trigger_error),
    url(
        r"^(?P<financial_year_id>\d{4}-\d{2})" "/focus/(?P<focus_slug>[\w-]+)/?$",
        cache_page(CACHE_MINUTES_SECS)(views.focus_area_preview),
        name="focus",
    ),
    url(
        r"^json/(?P<financial_year_id>\d{4}-\d{2})" "/focus.json",
        cache_page(CACHE_DAYS_SECS)(views.focus_preview_json),
        name="focus-json",
    ),
    # National and provincial treemap data
    url(
        r"^json/(?P<financial_year_id>\d{4}-\d{2})"
        "/(?P<sphere_slug>[\w-]+)"
        "/(?P<phase_slug>[\w-]+).json",
        cache_page(CACHE_DAYS_SECS)(views.treemaps_json),
    ),
    # Preview pages
    url(
        r"^(?P<financial_year_id>\d{4}-\d{2})"
        "/previews"
        "/(?P<sphere_slug>[\w-]+)"
        "/(?P<government_slug>[\w-]+)"
        "/(?P<department_slug>[\w-]+)$",
        cache_page(CACHE_MINUTES_SECS)(views.department_preview),
        name="department-preview",
    ),
    url(
        r"^json/(?P<financial_year_id>\d{4}-\d{2})"
        "/previews"
        "/(?P<sphere_slug>[\w-]+)"
        "/(?P<government_slug>[\w-]+)"
        "/(?P<phase_slug>[\w-]+).json",
        cache_page(CACHE_DAYS_SECS)(views.department_preview_json),
        name="department-preview-json",
    ),
    # Consolidated
    url(
        r"^json/(?P<financial_year_id>\d{4}-\d{2})" "/consolidated.json",
        cache_page(CACHE_DAYS_SECS)(views.consolidated_treemap_json),
        name="consolidated-json",
    ),
    # Homepage
    url(r"^$", cache_page(CACHE_MINUTES_SECS)(views.homepage), name="home"),
    # Search results
    url(
        r"^json/static-search.json",
        cache_page(CACHE_DAYS_SECS)(views.static_search_data),
    ),
    # Department list as CSV
    url(
        r"^(?P<financial_year_id>\d{4}-\d{2})" "/departments.csv$",
        cache_page(CACHE_MINUTES_SECS)(views.department_list_csv),
    ),
    # Department list for sphere as CSV
    url(
        r"^(?P<financial_year_id>\d{4}-\d{2})"
        "/(?P<sphere_slug>[\w-]+)"
        "/departments.csv$",
        cache_page(CACHE_MINUTES_SECS)(views.department_list_for_sphere_csv),
    ),
    # Programme list as CSV
    url(
        r"^(?P<financial_year_id>\d{4}-\d{2})"
        "/(?P<sphere_slug>[\w-]+)"
        "/programmes.csv$",
        cache_page(CACHE_MINUTES_SECS)(views.programme_list_csv),
    ),
    # Authentication
    url(r"^accounts/email.*", permission_denied),
    url(r"^accounts/", include("allauth.urls")),
    # SSO Provider
    url(r"^(?P<client_id>\w+)/sso$", cache_page(0)(sso)),
    # CSV
    url(
        r"^csv/$",
        cache_page(CACHE_DAYS_SECS)(views.openspending_csv),
        name="openspending_csv",
    ),
    # Admin
    url(r"^admin/", admin.site.urls),
    url(r"^admin/bulk_upload/template", bulk_upload.template_view),
    # Budget Portal
    url(r"^about/?$", cache_page(CACHE_DAYS_SECS)(views.about), name="about"),
    url(r"^events/?$", cache_page(CACHE_MINUTES_SECS)(views.events), name="events"),
    url(
        r"^learning-resources/?$",
        lambda request: redirect("/learning-resources/videos/", permanent=True),
        name="learning-resources",
    ),
    url(r"^learning-resources/videos/?$", cache_page(CACHE_MINUTES_SECS)(views.videos), name="videos"),
    url(
        r"^terms-and-conditions/?$",
        cache_page(CACHE_DAYS_SECS)(views.terms_and_conditions),
        name="terms-and-conditions",
    ),
    url(
        r"^learning-resources/resources/?$", cache_page(CACHE_DAYS_SECS)(views.resources), name="resources"
    ),
    url(
        r"^learning-resources/glossary/?$", cache_page(CACHE_MINUTES_SECS)(views.glossary), name="glossary"
    ),
    url(r"^faq/?$", cache_page(CACHE_MINUTES_SECS)(views.faq), name="faq"),
    url(
        r"^learning-resources/guides/?$",
        cache_page(CACHE_MINUTES_SECS)(views.guides),
        name="guides",
        kwargs={"slug": "index"},
    ),
    url(
        r"^learning-resources/guides/(?P<slug>[-\w]+)/?$",
        cache_page(CACHE_MINUTES_SECS)(views.guides),
        name="guide-list",
    ),
    # Dataset category list
    url(
        r"^datasets/?$",
        cache_page(CACHE_MINUTES_SECS)(views.dataset_category_list_page),
        name="dataset-landing-page",
    ),
    # Dataset categories
    url(
        r"^datasets/contributed/?$",
        cache_page(CACHE_MINUTES_SECS)(views.contributed_datasets_list),
        name="contributed-datasets",
    ),
    url(
        r"^datasets/contributed/(?P<dataset_slug>[-\w]+)/?$",
        cache_page(CACHE_MINUTES_SECS)(views.contributed_dataset),
        name="contributed-dataset",
    ),
    url(
        r"^datasets/(?P<category_slug>[-\w]+)/?$",
        cache_page(CACHE_MINUTES_SECS)(views.dataset_category_page),
        name="dataset-category",
    ),
    # Detaset detail
    url(
        r"^datasets/(?P<category_slug>[-\w]+)/(?P<dataset_slug>[-\w]+)/?$",
        cache_page(CACHE_MINUTES_SECS)(views.dataset_page),
        name="dataset",
    ),
    url(
        r"^(?P<financial_year_id>\d{4}-\d{2})/search-result/?$",
        cache_page(CACHE_MINUTES_SECS)(views.search_result),
        name="search-result",
    ),
    # Infrastructure projects
    url(
        r"^infrastructure-projects/?$",
        cache_page(CACHE_MINUTES_SECS)(views.infrastructure_project_list),
        name="infrastructure-project-list",
    ),
    url(
        r"^json/infrastructure-projects.json$",
        cache_page(CACHE_MINUTES_SECS)(views.infrastructure_projects_overview_json),
    ),
    url(
        r"^json/infrastructure-projects/(?P<project_slug>[\w-]+).json$",
        cache_page(CACHE_MINUTES_SECS)(views.infrastructure_project_detail_json),
    ),
    url(
        r"^infrastructure-projects/(?P<project_slug>[\w-]+)$",
        cache_page(CACHE_MINUTES_SECS)(views.infrastructure_project_detail),
        name="infrastructure-projects",
    ),
    # Department List
    url(
        r"^(?P<financial_year_id>\d{4}-\d{2})/departments$",
        cache_page(CACHE_MINUTES_SECS)(views.department_list),
        name="department-list",
    ),
    # Department detail
    # - National
    url(
        r"^(?P<financial_year_id>\d{4}-\d{2})/national/departments/(?P<department_slug>[\w-]+)/",
        include((department_urlpatterns, "national"), namespace="national"),
        kwargs={"sphere_slug": "national", "government_slug": "south-africa"},
        name="national-department",
    ),
    # - Provincial
    url(
        r"^(?P<financial_year_id>[\w-]+)"
        "/(?P<sphere_slug>[\w-]+)"
        "/(?P<government_slug>[\w-]+)"
        "/departments"
        "/(?P<department_slug>[\w-]+)/",
        include((department_urlpatterns, "provincial"), namespace="provincial"),
    ),
    url(r"^robots\.txt$", views.robots,),
    # Sitemap
    url(
        r"^sitemap\.xml$",
        cache_page(CACHE_DAYS_SECS)(sitemap_views.index),
        {"sitemaps": sitemaps},
    ),
    url(
        r"^sitemap-(?P<section>.+)\.xml$",
        cache_page(CACHE_DAYS_SECS)(sitemap_views.sitemap),
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    url("^", include(webflow_urls.urlpatterns)),
]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns
