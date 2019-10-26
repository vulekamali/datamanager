from django.conf.urls import url, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(
    "infrastructure-projects/provincial/search",
    views.ProvInfraProjectSearchView,
    base_name="provincial-infrastructure-project-api",
)

urlpatterns = [
    url(
        r"^infrastructure-projects/provincial/?$",
        views.provincial_infrastructure_project_list,
        name="provincial-infra-project-list",
    ),
    url(
        r"^infrastructure-projects/provincial/(?P<IRM_project_id>\d+)-(?P<slug>[\w-]+)$",
        views.provincial_infrastructure_project_detail,
        name="provincial-infra-project-detail",
    ),
    url(r"^api/v1/", include(router.urls)),
]
