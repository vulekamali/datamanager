from adminplus.sites import AdminSitePlus
from discourse.views import sso
from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin
from django.contrib.sitemaps import views as sitemap_views
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.views.decorators.cache import cache_page
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from . import bulk_upload, views
from .sitemaps import sitemaps
from .webflow import urls as webflow_urls

admin.site = AdminSitePlus()
admin.autodiscover()

CACHE_MINUTES_SECS = 60 * 5  # minutes


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
        cache_page(CACHE_MINUTES_SECS)(views.department_viz_subprog_treemap),
        name="department-viz-subprog-treemap",
    ),
    url(
        r"^viz/subprog-econ4-circles$",
        cache_page(CACHE_MINUTES_SECS)(views.department_viz_subprog_econ4_circles),
        name="department-viz-subprog-econ4-circles",
    ),
    url(
        r"^viz/subprog-econ4-bars$",
        cache_page(CACHE_MINUTES_SECS)(views.department_viz_subprog_econ4_bars),
        name="department-viz-subprog-econ4-bars",
    ),
]

public_entity_urlpatterns = [
    url(
        r"^$", cache_page(CACHE_MINUTES_SECS)(views.public_entity_page), name="public-entity"
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
        cache_page(CACHE_MINUTES_SECS)(views.focus_preview_json),
        name="focus-json",
    ),
    # National and provincial treemap data
    url(
        r"^json/(?P<financial_year_id>\d{4}-\d{2})"
        "/(?P<sphere_slug>[\w-]+)"
        "/(?P<phase_slug>[\w-]+).json",
        cache_page(CACHE_MINUTES_SECS)(views.treemaps_json),
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
        cache_page(CACHE_MINUTES_SECS)(views.department_preview_json),
        name="department-preview-json",
    ),
    # Consolidated
    url(
        r"^json/(?P<financial_year_id>\d{4}-\d{2})" "/consolidated.json",
        cache_page(CACHE_MINUTES_SECS)(views.consolidated_treemap_json),
        name="consolidated-json",
    ),
    # Homepage
    url(r"^$", cache_page(CACHE_MINUTES_SECS)(views.homepage), name="home"),
    # Search results
    url(
        r"^json/static-search.json",
        cache_page(CACHE_MINUTES_SECS)(views.static_search_data),
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
        cache_page(CACHE_MINUTES_SECS)(views.openspending_csv),
        name="openspending_csv",
    ),
    # Admin
    url(r"^admin/", admin.site.urls),
    url(r"^admin/bulk_upload/template", bulk_upload.template_view),
    # Budget Portal
    url(r"^about/?$", cache_page(CACHE_MINUTES_SECS)(views.about), name="about"),
    url(r"^events/?$", cache_page(CACHE_MINUTES_SECS)(views.events), name="events"),
    url(
        r"^learning-resources/?$",
        lambda request: redirect("/learning-resources/videos/", permanent=True),
        name="learning-resources",
    ),
    url(
        r"^learning-resources/videos/?$",
        cache_page(CACHE_MINUTES_SECS)(views.videos),
        name="videos",
    ),
    url(
        r"^terms-and-conditions/?$",
        cache_page(CACHE_MINUTES_SECS)(views.terms_and_conditions),
        name="terms-and-conditions",
    ),
    url(
        r"^learning-resources/resources/?$",
        cache_page(CACHE_MINUTES_SECS)(views.resources),
        name="resources",
    ),
    url(
        r"^learning-resources/glossary/?$",
        cache_page(CACHE_MINUTES_SECS)(views.glossary),
        name="glossary",
    ),
    url(r"^faq/?$", cache_page(CACHE_MINUTES_SECS)(views.faq), name="faq"),
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
        r"^latest/departments$",
        views.latest_department_list,
        name="latest-department-list",
    ),
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
    # Public Entities List
    url(
        r"^latest/public-entities$",
        views.latest_public_entity_list,
        name="latest-public-entity-list",
    ),
    url(
        r"^(?P<financial_year_id>\d{4}-\d{2})/public-entities$",
        cache_page(CACHE_MINUTES_SECS)(views.public_entity_list),
        name="public-entity-list",
    ),
    # Public Entity detail
    # - National
    url(
        r"^(?P<financial_year_id>\d{4}-\d{2})/national/public-entities/(?P<public_entity_slug>[\w-]+)/",
        include((public_entity_urlpatterns, "national"), namespace="national"),
        kwargs={"sphere_slug": "national", "government_slug": "south-africa"},
        name="national-public-entity",
    ),
    url(
        r"^robots\.txt$",
        views.robots,
    ),
    # Performance app
    path("performance/", include("performance.urls")),
    # IYM app
    path("iym/", include("iym.urls")),
    # Budget summary
    url(
        r"^budget-summary/?$",
        cache_page(CACHE_MINUTES_SECS)(views.budget_summary_view),
        name="budget-summary",
    ),
    # Budget comparison
    url(
        r"actual-expenditure/",
        views.iym_datasets_json,
        name="actual-expenditure",
    ),
    # Sitemap
    url(
        r"^sitemap\.xml$",
        cache_page(CACHE_MINUTES_SECS)(sitemap_views.index),
        {"sitemaps": sitemaps},
    ),
    url(
        r"^sitemap-(?P<section>.+)\.xml$",
        cache_page(CACHE_MINUTES_SECS)(sitemap_views.sitemap),
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # Public Entities List
    url(
        r"^public-entities$",
        views.public_entity_list,
        name="public-entity-list",
    ),
    url("^", include(webflow_urls.urlpatterns)),
    re_path(r"^cms/", include(wagtailadmin_urls)),
    re_path(r"^documents/", include(wagtaildocs_urls)),
    re_path(r"^", include(wagtail_urls)),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns
