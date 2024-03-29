from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files import File
from iym.models import IYMFileUpload
from budgetportal.models.government import FinancialYear
from django.conf import settings

import os
import iym.tasks
import mock

USERNAME = "testuser"
EMAIL = "testuser@domain.com"
PASSWORD = "12345"


class MockResponse:
    def __init__(self, json_data, status_code, text):
        self.json_data = json_data
        self.status_code = status_code
        self.text = text

    def json(self):
        return self.json_data

    def raise_for_status(self):
        return None


def mocked_requests_get(*args, **kwargs):
    if f"{settings.OPENSPENDING_HOST}/user/authorize" in args[0]:
        return MockResponse({"token": "test token"}, 200, "")
    elif f"{settings.OPENSPENDING_HOST}/package/status?" in args[0]:
        return MockResponse({"progress": 1, "status": "done"}, 200, "")
    elif args[0] == "https://test-upload-url.com/data_package.json?":
        return MockResponse({"name": "mock datapackage"}, 200, "")

    raise Exception(f"Unmocked GET request {args}")


def mocked_requests_put(*args, **kwargs):
    if (
        f"{settings.OPENSPENDING_HOST}/package/upload?datapackage=https%3A%2F%2Ftest-upload-url.com%2Fdata_package.json&jwt=test+token"
        in args[0]
    ):
        return MockResponse({"status": "0.0"}, 200, "initial status")
    elif "https://test-upload-url.com/test_data.csv" in args[0]:
        return MockResponse({"test": "file"}, 200, "")
    elif args[0] == "https://test-upload-url.com/data_package.json?":
        return MockResponse({"name": "mock datapackage"}, 200, "")

    raise Exception(f"Unmocked PUT request {args}")


def mocked_requests_post(*args, **kwargs):
    if f"{settings.OPENSPENDING_HOST}/user/authenticate_api_key" in args[0]:
        assert "x-api-key" in kwargs["headers"]
        return MockResponse({"token": "fake.jwt.blah"}, 200, "")
    elif f"{settings.OPENSPENDING_HOST}/datastore/" in args[0]:
        return MockResponse(
            {
                "filedata": {
                    "test_data.csv": {
                        "md5": "LTP9Xtp/f8n2DrFWG2/h1g==",
                        "name": "test_data.csv",
                        "length": 2354098,
                        "upload_url": "https://test-upload-url.com/test_data.csv",
                        "upload_query": {},
                        "type": "application/octet-stream",
                    },
                    "data_package.json": {
                        "md5": "T57ewjs7A5m0f0fJfCW2Iw==",
                        "name": "data_package.json",
                        "length": 21510,
                        "upload_url": "https://test-upload-url.com/data_package.json",
                        "upload_query": {},
                        "type": "application/octet-stream",
                    },
                }
            },
            200,
            "",
        )
    elif (
        f"{settings.OPENSPENDING_HOST}/package/upload?datapackage=https%3A%2F%2Ftest-upload-url.com%2Fdata_package.json&jwt=test+token"
        in args[0]
    ):
        return MockResponse({"status": "0.0"}, 200, "initial status")

    raise Exception(f"Unmocked POST request {args}")


def mocked_wrong_requests_get(*args, **kwargs):
    if f"{settings.OPENSPENDING_HOST}/user/authorize" in args[0]:
        return MockResponse({"permissions": {}}, 200, "")

    raise Exception(f"Unmocked GET request {args}")


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

        self.ckan_patch = mock.patch("iym.tasks.ckan")
        self.CKANMockClass = self.ckan_patch.start()
        self.CKANMockClass.action.package_search.return_value = {"count": 0}
        self.CKANMockClass.action.package_create.return_value = {"id": "whatever"}
        self.CKANMockClass.action.resource_create.return_value = {}
        self.CKANMockClass.action.vocabulary_list.return_value = [
            {"name": "financial_years", "id": "a"},
            {"name": "spheres", "id": "b"},
        ]
        self.addCleanup(self.ckan_patch.stop)

    def tearDown(self):
        self.zip_file.close()

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    @mock.patch("requests.post", side_effect=mocked_requests_post)
    @mock.patch("requests.put", side_effect=mocked_requests_put)
    def test_uploading(self, mock_get, mock_post, mock_put):
        financial_year = FinancialYear.objects.create(slug="2021-22")
        test_element = IYMFileUpload.objects.create(
            user=self.superuser,
            file=self.zip_file,
            financial_year=financial_year,
            latest_quarter="Q1",
        )

        iym.tasks.process_uploaded_file(test_element.id)
        test_element.refresh_from_db()

        import_report_lines = test_element.import_report.split("\n")
        assert " - Cleaning CSV" in import_report_lines[0]
        assert " - Getting authorisation for datastore" in import_report_lines[1]
        assert " - Uploading CSV /tmp/" in import_report_lines[2]
        assert " - Creating and uploading datapackage.json" in import_report_lines[3]
        assert (
            " - Datapackage url: https://test-upload-url.com/data_package.json"
            in import_report_lines[4]
        )
        assert " - Starting import of uploaded datapackage." in import_report_lines[5]
        assert " - Initial status: initial status" in import_report_lines[6]
        assert (
            f" - Monitoring status until completion ({settings.OPENSPENDING_HOST}/package/status?datapackage=https%3A%2F%2Ftest-upload-url.com%2Fdata_package.json):"
            in import_report_lines[7]
        )
        assert test_element.status == "done"

    @mock.patch("requests.get", side_effect=mocked_wrong_requests_get)
    @mock.patch("requests.post", side_effect=mocked_requests_post)
    @mock.patch("requests.put", side_effect=mocked_requests_put)
    def test_uploading_with_wrong_token(self, mock_get, mock_post, mock_put):
        financial_year = FinancialYear.objects.create(slug="2021-22")
        test_element = IYMFileUpload.objects.create(
            user=self.superuser,
            file=self.zip_file,
            financial_year=financial_year,
            latest_quarter="Q1",
        )

        iym.tasks.process_uploaded_file(test_element.id)
        test_element.refresh_from_db()

        import_report_lines = test_element.import_report.split("\n")
        assert " - Cleaning CSV" in import_report_lines[0]
        assert (
            " - Getting authorisation for datastore" in import_report_lines[1]
        ), import_report_lines
        assert (
            " - Authorization with OpenSpending failed." in import_report_lines[2]
        ), import_report_lines
        assert test_element.status == "fail"
