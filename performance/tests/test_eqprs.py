from django.test import TestCase
from performance.admin import EQPRSFileUploadAdmin
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.contrib import admin
from performance.models import EQPRSFileUpload
from django.test import RequestFactory

USERNAME = "testuser"
EMAIL = "testuser@domain.com"
PASSWORD = "12345"


def get_mocked_request(superuser):
    request = RequestFactory().get('/get/request')
    request.method = 'GET'
    request.user = superuser
    return request


class EQPRSFileUploadTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(
            username=USERNAME,
            password=PASSWORD,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        self.mocked_request = get_mocked_request(self.superuser)

    def test_selected_user_is_current_user(self):
        ea = EQPRSFileUploadAdmin(EQPRSFileUpload, AdminSite())
        form = ea.get_form(self.mocked_request)
        default_user = form.base_fields['user'].queryset.first()

        self.assertEqual(default_user, self.superuser)

    def test_saving_without_file(self):
        ea = EQPRSFileUploadAdmin(EQPRSFileUpload, AdminSite())
        form = ea.get_form(self.mocked_request)
        print('========= aaa =========')
        errors = form.errors
        print(errors['user'].data[0].message)
        print('========= bbb =========')
