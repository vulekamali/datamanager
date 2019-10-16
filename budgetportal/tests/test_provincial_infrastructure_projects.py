import os
import random

from django.db.models import Q
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

random.seed(123456789)


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
        self.url = reverse("search-provincial-infrastructure-projects")
        self.province = u"Eastern Cape"
        self.status = u"Construction"
        self.source = u"Community Library Service Grant"
        self.department = u"Department 1"
        self.name = u"Project 1"
        self.municipality = u"Local 2"
        self.contractor = u"Contractor 3"

        self.provinces = ["Eastern Cape", "Free State","Gauteng","KwaZulu-Natal","Limpopo","Mpumalanga","North West","Northern Cape","Western Cape"]
        self.statuses = ["Design", "Tender", "Feasibility", "Construction"]
        self.sources = ["Equitable Share", "Education Infrastructure Grant", "Community Library Service Grant"]
        for i in range(30):
            ProvInfraProject.objects.create(
                financial_year=self.fin_year,
                IRM_project_id=i,
                name="Project {}".format(i),
                department="Department {}".format(i),
                local_municipality="Local {}".format(i),
                district_municipality="District {}".format(i),
                province=random.choice(self.provinces),
                status=random.choice(self.statuses),
                primary_funding_source=random.choice(self.sources),
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
        project = ProvInfraProject.objects.get(department=self.department)

        data = {"department": self.department}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = len(response.data["results"])
        response_data = response.data["results"][0]
        self.assertEqual(number_of_projects, 1)
        self.assertEqual(response_data["name"], project.name)
        self.assertEqual(response_data["province"], project.province)
        self.assertEqual(response_data["local_municipality"], project.local_municipality)
        self.assertEqual(response_data["district_municipality"], project.district_municipality)

    def test_filter_by_province(self):
        projects = ProvInfraProject.objects.filter(province=self.province)

        data = {"province": self.province}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = len(response.data["results"])
        self.assertEqual(number_of_projects, projects.count())

    def test_filter_by_status(self):
        projects = ProvInfraProject.objects.filter(status=self.status)

        data = {"status": self.status}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = len(response.data["results"])
        self.assertEqual(number_of_projects, projects.count())

    def test_filter_by_funding_source(self):
        projects = ProvInfraProject.objects.filter(primary_funding_source=self.source)

        data = {"primary_funding_source": self.source}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = len(response.data["results"])
        self.assertEqual(number_of_projects, projects.count())

    def test_search_by_project_name(self):
        data = {"search": self.name}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.name)

    def test_search_by_municipality(self):
        data = {"search": self.municipality}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.municipality)

    def test_search_by_province(self):
        data = {"search": self.province}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.province)

    def test_search_by_contractor(self):
        data = {"search": self.contractor}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.contractor)

    def test_project_detail_content(self):
        project = ProvInfraProject.objects.first()
        args = [project.IRM_project_id, str(project.name).replace(" ", "-")]
        url = reverse("provincial-infra-project-detail", args=args)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, project.name)
