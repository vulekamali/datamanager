from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views

CACHE_SECS = 12 * 60 * 60


urlpatterns = [
    # Department List
    url(r'^(?P<financial_year_id>[\w-]+)'
        '/departments.yaml', cache_page(CACHE_SECS)(views.department_list)),
]
