from django.conf.urls import url, include
from django.views.decorators.cache import cache_page
from django.contrib import admin
from adminplus.sites import AdminSitePlus
from discourse.views import sso
from . import views

admin.site = AdminSitePlus()
admin.autodiscover()

from registration.forms import RegistrationFormUniqueEmail
from registration.backends.hmac.views import RegistrationView

CACHE_SECS = 0


urlpatterns = [

    # Home Page
    url(r'^(?P<financial_year_id>\d{4}-\d{2}).yaml$',
        cache_page(CACHE_SECS)(views.home)),

    # Search results
    url(r'^(?P<financial_year_id>\d{4}-\d{2})/search-result.yaml',
        cache_page(CACHE_SECS)(views.FinancialYearPage.as_view(
            slug='search-result',
        ))),

    # Department List
    url(r'^(?P<financial_year_id>\d{4}-\d{2})'
        '/departments.yaml', cache_page(CACHE_SECS)(views.department_list)),

    # Department
    url(r'^(?P<financial_year_id>\d{4}-\d{2})'
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
    url(r'^contributed-data.yaml', cache_page(CACHE_SECS)(views.contributed_dataset_list)),


    # Dataset
    url(r'^datasets'
        '/(?P<dataset_slug>[\w-]+).yaml$', cache_page(CACHE_SECS)(views.dataset)),


    # Admin
    url(r'^admin/', admin.site.urls),

    # Registration
    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=RegistrationFormUniqueEmail),
        name='registration_register'),
    url(r'^accounts/', include('registration.backends.hmac.urls')),

    # SSO
    url(r'^discourse/sso$', sso),

]
