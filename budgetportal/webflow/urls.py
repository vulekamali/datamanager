from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers

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
]
