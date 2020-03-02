from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(
    "infrastructure-projects/provincial/search",
    views.ProvInfraProjectSearchView,
    basename="provincial-infrastructure-project-api",
)

urlpatterns = [
    path(
        r"infrastructure-projects/provincial/",
        views.provincial_infrastructure_project_list,
        name="provincial-infra-project-list",
    ),
    path(
        r"infrastructure-projects/provincial/<int:id>-<slug:slug>",
        views.provincial_infrastructure_project_detail,
        name="provincial-infra-project-detail",
    ),
    path(
        r"infrastructure-projects/provincial/<int:id>-<slug:slug>/csv-download",
        views.ProvInfaProjectCSVDownload.as_view(),
        name="provincial-infra-project-detail-csv-download",
    ),
    path(r"api/v1/", include(router.urls)),
    path(
        "infrastructure-projects/provincial/search/csv",
        views.ProvInfraProjectSearchView.as_view({"get": "get_csv"}),
        name="provincial-infrastructure-project-api-csv",
    ),
]
