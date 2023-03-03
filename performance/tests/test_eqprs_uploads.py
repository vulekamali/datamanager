from django.test import TestCase
from performance.admin import EQPRSFileUploadAdmin
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.contrib import admin
from performance.models import EQPRSFileUpload, Indicator, EQPRSDepartmentAlias
from budgetportal.models.government import Department, Government, Sphere, FinancialYear
from django.test import RequestFactory
from performance import models
from django.core.files import File
from unittest.mock import Mock

import performance.admin
import os
import time

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
        file_path = os.path.abspath(("performance/tests/static/correct_data.csv"))
        national_file_path = os.path.abspath(
            ("performance/tests/static/national_data.csv")
        )
        wrong_report_type_file_path = os.path.abspath(
            ("performance/tests/static/wrong_report_type.csv")
        )
        data_for_deleting_indicators_path = os.path.abspath(
            ("performance/tests/static/data_for_deleting_indicators.csv")
        )
        department_name_containing_government_path = os.path.abspath(
            ("performance/tests/static/department_name_containing_government.csv")
        )
        self.csv_file = File(open(file_path, "rb"))
        self.national_file = File(open(national_file_path, "rb"))
        self.wrong_report_type_file = File(open(wrong_report_type_file_path, "rb"))
        self.data_for_deleting_indicators_file = File(
            open(data_for_deleting_indicators_path, "rb")
        )
        self.department_name_containing_government_file = File(
            open(department_name_containing_government_path, "rb")
        )
        self.mocked_request = get_mocked_request(self.superuser)

    def tearDown(self):
        self.csv_file.close()
        self.national_file.close()
        self.wrong_report_type_file.close()
        self.data_for_deleting_indicators_file.close()

    def test_report_name_validation(self):
        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser, file=self.wrong_report_type_file
        )
        performance.admin.save_imported_indicators(test_element.id)
        test_element.refresh_from_db()
        assert "Report type must be for one of" in test_element.import_report
        assert (
            "* Provincial Institutions Oversight Performance  Report"
            in test_element.import_report
        )
        assert (
            "* National Institutions Oversight Performance  Report"
            in test_element.import_report
        )

    def test_with_missing_department(self):
        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser, file=self.csv_file
        )
        fy = FinancialYear.objects.create(slug="2021-22")
        sphere = Sphere.objects.create(name="Provincial", financial_year=fy)
        government = Government.objects.create(name="Eastern Cape", sphere=sphere)
        department = Department.objects.create(
            name="HealthTest", government=government, vote_number=1
        )
        performance.admin.save_imported_indicators(test_element.id)
        test_element.refresh_from_db()
        assert test_element.num_not_imported == 2
        assert (
            "Department names that could not be matched on import :"
            in test_element.import_report
        )
        assert "* Health" in test_element.import_report

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

        indicator = models.Indicator.objects.all().first()
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

    def test_task_creation(self):
        fy = FinancialYear.objects.create(slug="2021-22")
        sphere = Sphere.objects.create(name="Provincial", financial_year=fy)
        government = Government.objects.create(name="Eastern Cape", sphere=sphere)
        department = Department.objects.create(
            name="Health", government=government, vote_number=1
        )

        model_admin = EQPRSFileUploadAdmin(
            model=EQPRSFileUpload, admin_site=AdminSite()
        )
        model_admin.save_model(
            obj=EQPRSFileUpload(file=self.csv_file),
            request=Mock(user=self.superuser),
            form=None,
            change=None,
        )

        last_element = EQPRSFileUpload.objects.all().last()
        assert last_element.task_id is not None

    def test_status_in_list_view(self):
        assert "processing_completed" in EQPRSFileUploadAdmin.list_display

        fy = FinancialYear.objects.create(slug="2021-22")
        sphere = Sphere.objects.create(name="Provincial", financial_year=fy)
        government = Government.objects.create(name="Eastern Cape", sphere=sphere)
        department = Department.objects.create(
            name="Health", government=government, vote_number=1
        )

        model_admin = EQPRSFileUploadAdmin(
            model=EQPRSFileUpload, admin_site=AdminSite()
        )
        model_admin.save_model(
            obj=EQPRSFileUpload(file=self.csv_file),
            request=Mock(user=self.superuser),
            form=None,
            change=None,
        )

        last_element = EQPRSFileUpload.objects.all().last()
        assert model_admin.processing_completed(last_element) == True

    def test_with_national_government(self):
        fy = FinancialYear.objects.create(slug="2021-22")
        sphere = Sphere.objects.create(name="Provincial", financial_year=fy)
        government = Government.objects.create(name="South Africa", sphere=sphere)
        department = Department.objects.create(
            name="Health", government=government, vote_number=1
        )

        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser, file=self.national_file
        )
        performance.admin.save_imported_indicators(test_element.id)
        test_element.refresh_from_db()

        assert test_element.import_report == ""
        assert test_element.num_imported == 1
        indicator = models.Indicator.objects.all().first()
        assert indicator.programme_name == "Programme 1: Administration"

    def test_with_alias(self):
        fy = FinancialYear.objects.create(slug="2021-22")
        sphere = Sphere.objects.create(name="Provincial", financial_year=fy)
        government = Government.objects.create(name="South Africa", sphere=sphere)
        department = Department.objects.create(
            name="Department to be found by its alias",
            government=government,
            vote_number=1,
        )
        EQPRSDepartmentAlias.objects.create(department=department, alias="Health")

        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser, file=self.national_file
        )
        performance.admin.save_imported_indicators(test_element.id)
        test_element.refresh_from_db()

        assert test_element.import_report == ""
        assert test_element.num_imported == 1
        indicator = models.Indicator.objects.all().first()
        assert indicator.programme_name == "Programme 1: Administration"
        assert indicator.department.name == "Department to be found by its alias"

    def test_deleting_old_indicators(self):
        """
        test that
          - if gov A and dept A is in the data, its old indicators for that
            financial year are deleted. Any other financial years remain
          - if Gov A, B and dept A, B is in the data, old indicators for Gov A
            DeptA are deleted but Gov A dept B are not deleted
        """

        fy = FinancialYear.objects.create(slug="2017-18")
        sphere = Sphere.objects.create(name="Provincial", financial_year=fy)

        government_1 = Government.objects.create(name="Eastern Cape", sphere=sphere)
        department_1 = Department.objects.create(
            name="Health",
            government=government_1,
            vote_number=1,
        )
        Indicator.objects.create(
            indicator_name="Test Indicator 1",
            department=department_1,
            source=EQPRSFileUpload.objects.create(user=self.superuser, file=None),
        )

        government_2 = Government.objects.create(name="Western Cape", sphere=sphere)
        department_2 = Department.objects.create(
            name="Education",
            government=government_2,
            vote_number=1,
        )
        Indicator.objects.create(
            indicator_name="Test Indicator 2",
            department=department_2,
            source=EQPRSFileUpload.objects.create(user=self.superuser, file=None),
        )

        department_3 = Department.objects.create(
            name="Health",
            government=government_2,
            vote_number=2,
        )
        Indicator.objects.create(
            indicator_name="Test Indicator 3",
            department=department_3,
            source=EQPRSFileUpload.objects.create(user=self.superuser, file=None),
        )

        assert Indicator.objects.all().count() == 3

        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser, file=self.data_for_deleting_indicators_file
        )
        performance.admin.save_imported_indicators(test_element.id)
        test_element.refresh_from_db()

        # ids 1 & 2 are deleted
        assert Indicator.objects.all().count() == 3

        # id 3 is remaining
        indicator_3 = Indicator.objects.get(id=3)
        assert indicator_3.indicator_name == "Test Indicator 3"
        assert indicator_3.department.name == "Health"
        assert indicator_3.department.government.name == "Western Cape"
        assert indicator_3.department.government.sphere.financial_year.slug == "2017-18"

        # new objects(with id 4 & 5) are created
        indicator_4 = Indicator.objects.get(id=4)
        assert (
            indicator_4.indicator_name
            == "9.1.2 Number of statutory documents tabled at Legislature"
        )
        assert indicator_4.department.name == "Health"
        assert indicator_4.department.government.name == "Eastern Cape"
        assert indicator_4.department.government.sphere.financial_year.slug == "2017-18"

        indicator_5 = Indicator.objects.get(id=5)
        assert (
            indicator_5.indicator_name
            == "6.4.1 Holistic Human  Resources for Health (HRH) strategy  approved "
        )
        assert indicator_5.department.name == "Education"
        assert indicator_5.department.government.name == "Western Cape"
        assert indicator_5.department.government.sphere.financial_year.slug == "2017-18"

    def test_department_name_containing_government(self):
        fy = FinancialYear.objects.create(slug="2021-22")
        sphere = Sphere.objects.create(name="Provincial", financial_year=fy)
        government = Government.objects.create(name="Eastern Cape", sphere=sphere)
        department = Department.objects.create(
            name="Health", government=government, vote_number=1
        )

        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser, file=self.department_name_containing_government_file
        )
        performance.admin.save_imported_indicators(test_element.id)
        test_element.refresh_from_db()
        assert Indicator.objects.all().count() == 2
