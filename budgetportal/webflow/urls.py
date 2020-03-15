from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers
from django.views.generic.base import RedirectView

from . import views

router = routers.DefaultRouter()
router.register(
    "infrastructure-projects/full/search",
    views.InfraProjectSearchView,
    basename="infrastructure-project-api",
)

urlpatterns = [
    path(
        r"infrastructure-projects/full/",
        views.infrastructure_project_list,
        name="infra-project-list",
    ),
    path(
        r"infrastructure-projects/full/<int:id>-<slug:slug>",
        views.infrastructure_project_detail,
        name="infra-project-detail",
    ),
    path(
        r"infrastructure-projects/full/<int:id>-<slug:slug>/csv-download",
        views.InfaProjectCSVDownload.as_view(),
        name="infra-project-detail-csv-download",
    ),
    path(r"api/v1/", include(router.urls)),
    path(
        "infrastructure-projects/full/search/csv",
        views.InfraProjectSearchView.as_view({"get": "get_csv"}),
        name="infrastructure-project-api-csv",
    ),
    # Redirect provincial/ to full/
    path(
        r"infrastructure-projects/provincial/",
        RedirectView.as_view(
            pattern_name="infra-project-list", query_string=True, permanent=True
        ),
        name="redirect-old-prov-infra-project-list",
    ),
    path(
        r"infrastructure-projects/provincial/<int:id>-<slug:slug>",
        RedirectView.as_view(
            pattern_name="infra-project-detail", query_string=True, permanent=True
        ),
        name="redirect-old-prov-infra-project-detail",
    ),
    path(
        r"infrastructure-projects/provincial/<int:id>-<slug:slug>/csv-download",
        RedirectView.as_view(
            pattern_name="infra-project-detail-csv-download",
            query_string=True,
            permanent=True,
        ),
        name="redirect-old-prov-infra-project-detail-csv-download",
    ),
    path(
        "infrastructure-projects/provincial/search/csv",
        RedirectView.as_view(
            pattern_name="infrastructure-project-api-csv",
            query_string=True,
            permanent=True,
        ),
        name="redirect-old-prov-infrastructure-project-api-csv",
    ),
    path(
        "api/v1/infrastructure-projects/provincial/search/",
        RedirectView.as_view(
            url="api/v1/infrastructure-projects/full/search/",
            query_string=True,
            permanent=True,
        ),
        name="redirect-old-prov-infrastructure-project-api",
    ),
    path(
        "api/v1/infrastructure-projects/provincial/search/facets/",
        RedirectView.as_view(
            url="api/v1/infrastructure-projects/full/search/facets/",
            query_string=True,
            permanent=True,
        ),
        name="redirect-old-prov-infrastructure-project-facet-api",
    ),
]
