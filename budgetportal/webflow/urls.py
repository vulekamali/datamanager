from django.conf.urls import url, include
from . import views

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
    url(
        r"^api/v1/infrastructure-projects/provincial/$",
        views.ProvInfraProjectView.as_view(),
        name="provincial-infrastructure-project-api",
    ),
]
