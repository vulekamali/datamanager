import os

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from selenium.webdriver.support.select import Select
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


class ProvInfraProjectSeleniumTestCase(BaseSeleniumTestCase):
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

        super(ProvInfraProjectSeleniumTestCase, self).setUp()

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

    def test_empty_rows_deleted(self):
        empty_row = [None] * self.report_sheet.data_set.width
        num_nonempty_rows = self.report_sheet.data_set.height
        num_of_empty_rows = 100
        for i in range(num_of_empty_rows):
            self.report_sheet.data_set.append(empty_row)

        total_rows = num_nonempty_rows + num_of_empty_rows
        self.assertEqual(self.report_sheet.data_set.height, total_rows)

        self.report_sheet.process()
        self.assertEqual(self.report_sheet.data_set.height, num_nonempty_rows)


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


class ProvInfraProjectAPITestCase(APITestCase):
    def setUp(self):
        """Create 30 Provincial Infrastructure Projects"""

        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.url = reverse("provincial-infrastructure-project-api")
        self.provinces = ["Eastern Cape", "Free State"]
        self.statuses = ["Design", "Construction"]
        self.sources = [
            "Education Infrastructure Grant",
            "Community Library Service Grant",
        ]
        for i in range(30):
            if i < 15:
                status = self.statuses[0]
                province = self.provinces[0]
                source = self.sources[0]
            else:
                status = self.statuses[1]
                province = self.provinces[1]
                source = self.sources[1]

            ProvInfraProject.objects.create(
                financial_year=self.fin_year,
                IRM_project_id=i,
                name="Project {}".format(i),
                department="Department {}".format(i),
                local_municipality="Local {}".format(i),
                district_municipality="District {}".format(i),
                province=province,
                status=status,
                primary_funding_source=source,
                main_contractor="Contractor {}".format(i),
                principle_agent="Principle Agent {}".format(i),
                program_implementing_agent="Program Agent {}".format(i),
                other_parties="Service Provider: XXXX{}".format(i),
            )

    def test_projects_per_page(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = len(response.data["results"])
        self.assertLessEqual(number_of_results, 20)

    def test_filter_by_department(self):
        department = "Department 1"
        project = ProvInfraProject.objects.get(department=department)

        data = {"department": department}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = len(response.data["results"])
        response_data = response.data["results"][0]
        self.assertEqual(number_of_projects, 1)
        self.assertEqual(response_data["name"], project.name)

    def test_filter_by_province(self):
        province = "Eastern Cape"
        data = {"province": province}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = len(response.data["results"])
        self.assertEqual(number_of_projects, 15)

    def test_filter_by_status(self):
        status_ = "Construction"
        data = {"status": status_}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = len(response.data["results"])
        self.assertEqual(number_of_projects, 15)

    def test_filter_by_funding_source(self):
        source = "Community Library Service Grant"
        data = {"primary_funding_source": source}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = len(response.data["results"])
        self.assertEqual(number_of_projects, 15)

    def test_search_by_project_name(self):
        name = "Project 1"
        data = {"search": name}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, name)

    def test_search_by_municipality(self):
        municipality = "Local 1"
        data = {"search": municipality}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, municipality)

    def test_search_by_province(self):
        province = "Eastern Cape"
        data = {"search": province}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, province)

    def test_search_by_contractor(self):
        contractor = "Contractor 3"
        data = {"search": contractor}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, contractor)

    def test_search_multiple_fields(self):
        ProvInfraProject.objects.create(
            financial_year=self.fin_year,
            IRM_project_id=12345,
            name="Something School",
            province="Eastern Cape",
        )
        data = {"search": "Eastern Cape School"}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]

        # There should be only one match because first 30 objects don't
        # have school word
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["province"], "Eastern Cape")
        self.assertEqual(results[0]["name"], "Something School")

    def test_create_project_failed(self):
        data = {"financial_year": self.fin_year, "IRM_project_id": 12345}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_change_project_failed(self):
        data = {
            "id": 1,
            "financial_year": self.fin_year,
            "IRM_project_id": 123456789,
            "status": "CHANGED",
        }
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_project_failed(self):
        data = {"id": 1}
        response = self.client.delete(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_url_path(self):
        name = "Project 10"
        data = {"search": name}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["results"][0]
        url = result["url"]

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, name)


class ProvInfraProjectContentTestCase(APITestCase):
    fixtures = ["test-prov-infra-project-content"]

    def test_project_detail_content(self):
        project = ProvInfraProject.objects.first()
        url = project.get_url_path(project)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, project.name)
