from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files import File
from iym.models import IYMFileUpload
from budgetportal.models.government import FinancialYear

import os
import iym.admin
import mock

USERNAME = "testuser"
EMAIL = "testuser@domain.com"
PASSWORD = "12345"


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        return None


def mocked_requests_get(*args, **kwargs):
    if "https://openspending-dedicated.vulekamali.gov.za/datastore/" in args[0]:
        return MockResponse({
            'test': 'emre'
        }, 200)
    elif "https://openspending-dedicated.vulekamali.gov.za/user/authorize" in args[0]:
        return MockResponse({
            'token': 'this is the test token'
        }, 200)
    elif "https://openspending-dedicated.vulekamali.gov.za/package/upload?" in args[0]:
        return MockResponse({
            'test': 'emre3'
        }, 200)

    return MockResponse(None, 404)


class IYMFileUploadTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(
            username=USERNAME,
            password=PASSWORD,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        test_file_path = os.path.abspath(("iym/tests/static/test_data.zip"))
        self.zip_file = File(open(test_file_path, "rb"))

    def tearDown(self):
        self.zip_file.close()

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_initial(self, mock_get):
        financial_year = FinancialYear.objects.create(slug="2021-22")
        test_element = IYMFileUpload.objects.create(
            user=self.superuser, file=self.zip_file, financial_year=financial_year, latest_quarter='Q1'
        )

        iym.admin.process_uploaded_file(test_element.id)
        test_element.refresh_from_db()

        print('============ xxx ============')
        print(test_element.import_report)
        print('============ yyy ============')
