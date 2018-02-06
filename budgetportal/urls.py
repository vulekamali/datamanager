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
    url(r'^(?P<financial_year_id>[\w-]+).yaml$', views.home),
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
