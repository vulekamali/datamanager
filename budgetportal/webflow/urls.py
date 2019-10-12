from django.conf.urls import url, include
from . import views

urlpatterns = [

    url(r'^infrastructure-projects/provincial$',
        views.provincial_infrastructure_project_list,
        name='provincial-infra-project-list'
    ),
    url(r'^infrastructure-projects/provincial/\w+$',
        views.provincial_infrastructure_project_detail,
        name='provincial-infra-project-detailo'
    ),
]
