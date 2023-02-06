from django.test import TestCase
from performance.admin import EQPRSFileUploadAdmin
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.contrib import admin
from performance.models import EQPRSFileUpload, Indicator
from budgetportal.models.government import Department, Government, Sphere, FinancialYear
from django.test import RequestFactory
from performance import models
from django.core.files import File

import performance.admin
import os

USERNAME = "testuser"
EMAIL = "testuser@domain.com"
PASSWORD = "12345"


def get_mocked_request(superuser):
    request = RequestFactory().get("/get/request")
    request.method = "GET"
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
        file_path = os.path.abspath(("performance/static/correct_data.csv"))
        wrong_report_type_file_path = os.path.abspath(
            ("performance/static/wrong_report_type.csv")
        )
        self.csv_file = File(open(file_path, "rb"))
        self.wrong_report_type_file = File(open(wrong_report_type_file_path, "rb"))
        self.mocked_request = get_mocked_request(self.superuser)

    def tearDown(self):
        self.csv_file.close()
        self.wrong_report_type_file.close()

    def test_report_name_validation(self):
        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser, file=self.wrong_report_type_file
        )
        performance.admin.save_imported_indicators(test_element.id)
        test_element.refresh_from_db()
        assert (
            test_element.import_report
            == """Report type must be for one of
* Provincial Institutions Oversight Performance  Report
* National Institutions Oversight Performance  Report
"""
        )

    def test_with_missing_department(self):
        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser, file=self.csv_file
        )
        performance.admin.save_imported_indicators(test_element.id)
        test_element.refresh_from_db()
        assert test_element.num_not_imported == 2
        assert (
            test_element.import_report
            == """Department names that could not be matched on import :
* Health
"""
        )

    def test_with_correct_csv(self):
        fy = FinancialYear.objects.create(slug="2021-22")
        sphere = Sphere.objects.create(name="Provincial", financial_year=fy)
        government = Government.objects.create(name="Eastern Cape", sphere=sphere)
        department = Department.objects.create(
            name="Health", government=government, vote_number=1
        )

        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser, file=self.csv_file
        )
        performance.admin.save_imported_indicators(test_element.id)
        test_element.refresh_from_db()
        assert Indicator.objects.all().count() == 2

        indicator = models.Indicator.objects.filter(id=1).first()
        assert test_element.import_report == ""
        assert test_element.num_imported == 2
        assert (
            indicator.indicator_name
            == "9.1.2 Number of statutory documents tabled at Legislature"
        )
        assert indicator.sector == "Health"
        assert indicator.programme_name == "Programme 1: Administration"
        assert indicator.subprogramme_name == "Sub-Programme 1.1: Office of the MEC"
        assert indicator.frequency == "quarterly"
        assert indicator.type == "Non-Standardized"
        assert indicator.subtype == "Max"
        assert indicator.mtsf_outcome == "Priority 3: Education, Skills And Health"
        assert (
            indicator.cluster
            == "The Social Protection, Community and Human Development cluster"
        )

        assert indicator.q1_target == "0"
        assert indicator.q1_actual_output == "0"
        assert indicator.q1_deviation_reason == "There is no target for quarter one"
        assert indicator.q1_corrective_action == ""
        assert indicator.q1_national_comments == ""
        assert indicator.q1_otp_comments == ""
        assert indicator.q1_dpme_coordinator_comments == ""
        assert indicator.q1_treasury_comments == ""

        assert indicator.q2_target == "1"
        assert indicator.q2_actual_output == "2"
        assert indicator.q2_deviation_reason == "Target achieved"
        assert indicator.q2_corrective_action == ""
        assert indicator.q2_national_comments == ""
        assert indicator.q2_otp_comments == ""
        assert indicator.q2_dpme_coordinator_comments == ""
        assert indicator.q2_treasury_comments == ""

        assert indicator.q3_target == "2"
        assert indicator.q3_actual_output == "2"
        assert indicator.q3_deviation_reason == "Target achieved"
        assert indicator.q3_corrective_action == ""
        assert indicator.q3_national_comments == ""
        assert indicator.q3_otp_comments == ""
        assert indicator.q3_dpme_coordinator_comments == ""
        assert indicator.q3_treasury_comments == ""

        assert indicator.q4_target == "5"
        assert indicator.q4_actual_output == "8"
        assert indicator.q4_deviation_reason == "All statutory documents submitted."
        assert indicator.q4_corrective_action == ""
        assert indicator.q4_national_comments == ""
        assert indicator.q4_otp_comments == ""
        assert indicator.q4_dpme_coordinator_comments == ""
        assert indicator.q4_treasury_comments == ""

        assert indicator.annual_target == "8"
        assert indicator.annual_aggregate_output == ""
        assert indicator.annual_pre_audit_output == "8"
        assert indicator.annual_deviation_reason == "Target achieved "
        assert indicator.annual_corrective_action == ""
        assert indicator.annual_otp_comments == ""
        assert indicator.annual_national_comments == ""
        assert indicator.annual_dpme_coordinator_comments == ""
        assert indicator.annual_treasury_comments == ""
        assert indicator.annual_audited_output == ""
