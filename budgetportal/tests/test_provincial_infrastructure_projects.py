import os

from django.test import TestCase
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from tablib import Dataset

from budgetportal.models import FinancialYear, ProvInfraProject
from budgetportal.provincial_infrastructure_projects import (
    NORMAL_HEADERS,
    IRMReportSheet,
)
from budgetportal.tests.helpers import BaseSeleniumTestCase

USERNAME = "testuser"
EMAIL = "testuser@domain.com"
PASSWORD = "12345"


class ProvInfraProjectsTestCase(BaseSeleniumTestCase):
    def setUp(self):
        user = User.objects.create_user(
            username=USERNAME,
            password=PASSWORD,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        EmailAddress.objects.create(user=user, email=EMAIL, verified=True)
        self.path = os.path.dirname(__file__)
        self.financial_year = FinancialYear.objects.create(slug="2019-20")
        self.timeout = 10

        super(ProvInfraProjectsTestCase, self).setUp()

    def test_upload_xlsx_for_prov_infra_projects(self):
        filename = "budgetportal/tests/test_data/test_import_prov_infra_projects.xlsx"

        selenium = self.selenium

        # Login
        selenium.get("%s%s" % (self.live_server_url, "/admin/"))
        username = selenium.find_element_by_id("id_login")
        password = selenium.find_element_by_id("id_password")
        submit_button = selenium.find_element_by_css_selector('button[type="submit"]')
        username.send_keys(EMAIL)
        password.send_keys(PASSWORD)
        submit_button.click()

        selenium.find_element_by_link_text("Prov infra projects").click()
        selenium.find_element_by_link_text("IMPORT").click()

        file_import = selenium.find_element_by_id("id_import_file")
        financial_year_select = Select(selenium.find_element_by_id("id_financial_year"))
        file_import.send_keys(os.path.abspath(filename))
        financial_year_select.select_by_value(str(self.financial_year.id))
        selenium.find_element_by_css_selector('input[type="submit"]').click()

        selenium.implicitly_wait(self.timeout)
        selenium.find_element_by_name("confirm").click()

        selenium.implicitly_wait(self.timeout)
        selenium.find_element_by_class_name("success")

        # check values of the first project
        first_project = ProvInfraProject.objects.get(IRM_project_id=30682)
        self.assertEqual(first_project.financial_year.slug, "2019-20")
        self.assertEqual(first_project.project_number, "W/50042423/WS")
        self.assertEqual(first_project.name, "BLUE JUNIOR SECONDARY SCHOOL")
        self.assertEqual(first_project.project_expenditure_total, 1315479)

        # check whether null values are imported as null, and 0 imported as 0
        self.assertEqual(first_project.contracted_construction_end_date, None)
        self.assertEqual(
            first_project.expenditure_from_previous_years_construction_costs, None
        )
        self.assertEqual(first_project.variation_orders, 0)

        # check whether parties/contractor mapping worked correctly
        self.assertEqual(first_project.program_implementing_agent, "DOPW")
        self.assertEqual(first_project.other_parties, None)

        # check whether all rows imported (There are 11 rows)
        count = ProvInfraProject.objects.count()
        self.assertEqual(count, 11)


class IRMReportSheetTestCase(TestCase):
    def setUp(self):
        dataset = Dataset()
        dataset.headers = NORMAL_HEADERS + ["Project Contractor"] * 50
        row = (
            [1] * len(NORMAL_HEADERS)
            + [
                "Program Implementing Agent: DOPW",
                "Program Implementing Agent: TEST",
                "Main Contractor: AAAA",
                "Principal Agent: BBBB",
            ]
            + [None] * 46
        )
        dataset.append(row=row)
        self.report_sheet = IRMReportSheet(dataset)

    def test_clean_project_contractors(self):
        """Check that first dataset has 50 Project Contractor columns but output has 0"""

        report_sheet = self.report_sheet
        num_project_contractor_columns = len(report_sheet.contractor_columns)
        self.assertEqual(num_project_contractor_columns, 50)

        report_sheet.process()
        new_report_sheet = IRMReportSheet(report_sheet.output_data_set)

        num_project_contractor_columns = len(new_report_sheet.contractor_columns)
        self.assertEqual(num_project_contractor_columns, 0)

    def test_assigned_correctly(self):
        """Check that project contractors successfully mapped"""

        self.report_sheet.process()
        program_implementing_agent = self.report_sheet.output_data_set[
            "Program Implementing Agent"
        ]
        main_contractor = self.report_sheet.output_data_set["Main Contractor"]
        principal_agent = self.report_sheet.output_data_set["Principal Agent"]
        other_parties = self.report_sheet.output_data_set["Other parties"]

        self.assertEqual(program_implementing_agent, ["DOPW\nTEST"])
        self.assertEqual(main_contractor, ["AAAA"])
        self.assertEqual(principal_agent, ["BBBB"])
        self.assertEqual(other_parties, [None])


class IRMReportSheetWithOtherKeysTestCase(TestCase):
    def setUp(self):
        dataset_with_other_keys = Dataset()
        dataset_with_other_keys.headers = NORMAL_HEADERS + ["Project Contractor"] * 50
        row_with_other_keys = (
            [1] * len(NORMAL_HEADERS)
            + [
                "Service Provider: DOPW",
                "Program Implementing Agent: TEST",
                "Service Provider: AAAA",
                "Principal Agent: BBBB",
            ]
            + [None] * 46
        )
        dataset_with_other_keys.append(row_with_other_keys)
        self.sheet_with_other_keys = IRMReportSheet(dataset_with_other_keys)

    def test_other_parties(self):
        """Checks when different keys given in project contractor"""

        self.sheet_with_other_keys.process()

        program_implementing_agent = self.sheet_with_other_keys.output_data_set[
            "Program Implementing Agent"
        ]
        main_contractor = self.sheet_with_other_keys.output_data_set["Main Contractor"]
        principal_agent = self.sheet_with_other_keys.output_data_set["Principal Agent"]
        other_parties = self.sheet_with_other_keys.output_data_set["Other parties"]

        self.assertEqual(program_implementing_agent, ["TEST"])
        self.assertEqual(main_contractor, [None])
        self.assertEqual(principal_agent, ["BBBB"])
        self.assertEqual(
            other_parties, ["Service Provider: DOPW\nService Provider: AAAA"]
        )
