import os
from datetime import date, timedelta

from django.core.files import File
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APITransactionTestCase
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from selenium.webdriver.support.select import Select
from tablib import Dataset
import unittest

from budgetportal.models import (
    FinancialYear,
    ProvInfraProject,
    ProvInfraProjectSnapshot,
    IRMSnapshot,
    Quarter,
)
from budgetportal import irm_preprocessor
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
        self.quarter = Quarter.objects.create(number=1)
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

        # check whether parties/implementor mapping worked correctly
        self.assertEqual(first_project.program_implementing_agent, "DOPW")
        self.assertEqual(first_project.other_parties, None)

        # check whether all rows imported (There are 11 rows)
        count = ProvInfraProject.objects.count()
        self.assertEqual(count, 11)

    def test_import_irm_snapshot(self):
        # TODO: not completed yet
        filename = "budgetportal/tests/test_data/test_import_prov_infra_projects2.xlsx"

        selenium = self.selenium

        # Login
        selenium.get("%s%s" % (self.live_server_url, "/admin/"))
        username = selenium.find_element_by_id("id_login")
        password = selenium.find_element_by_id("id_password")
        submit_button = selenium.find_element_by_css_selector('button[type="submit"]')
        username.send_keys(EMAIL)
        password.send_keys(PASSWORD)
        submit_button.click()

        selenium.find_element_by_link_text("IRM Snapshots").click()
        selenium.find_element_by_link_text("ADD IRM SNAPSHOT").click()

        financial_year_select = Select(selenium.find_element_by_id("id_financial_year"))
        quarter_select = Select(selenium.find_element_by_id("id_quarter"))
        file_import = selenium.find_element_by_id("id_file")

        selenium.find_element_by_link_text("Today").click()
        selenium.find_element_by_link_text("Now").click()
        financial_year_select.select_by_value(str(self.financial_year.id))
        quarter_select.select_by_value(str(self.quarter.id))
        file_import.send_keys(os.path.abspath(filename))

        selenium.find_element_by_css_selector('input[value="Save"]').click()
        selenium.implicitly_wait(self.timeout)


class ProvInfraProjectAPITestCase(APITransactionTestCase):
    def setUp(self):
        """Create 30 Provincial Infrastructure Projects"""

        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=1)
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.provinces = ["Eastern Cape", "Free State"]
        self.statuses = ["Design", "Construction"]
        self.sources = [
            "Education Infrastructure Grant",
            "Community Library Service Grant",
        ]
        name = "budgetportal/tests/test_data/test_import_prov_infra_projects.xlsx"
        random_date = date.today() + timedelta(days=5)

        self.irm_snapshot = IRMSnapshot()
        self.irm_snapshot.date_taken = random_date
        self.irm_snapshot.financial_year = self.fin_year
        self.irm_snapshot.quarter = self.quarter
        self.irm_snapshot.file.name = name
        self.irm_snapshot.save()
        irm_snapshot = IRMSnapshot.objects.first()
        for i in range(30):
            if i < 15:
                status = self.statuses[0]
                province = self.provinces[0]
                source = self.sources[0]
            else:
                status = self.statuses[1]
                province = self.provinces[1]
                source = self.sources[1]
            project = ProvInfraProject.objects.create(IRM_project_id=i)
            ProvInfraProjectSnapshot.objects.create(
                irm_snapshot=irm_snapshot,
                project=project,
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
                estimated_completion_date=random_date,
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

    def test_url_path(self):
        name = "Project 10"
        data = {"search": name}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["results"][0]
        url_path = result["url_path"]

        response = self.client.get(url_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, name)


class ProvInfraProjectContentTestCase(APITestCase):
    fixtures = ["test-prov-infra-project-content"]

    def test_project_detail_content(self):
        project = ProvInfraProject.objects.first()
        url = project.get_absolute_url()
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, project.name)


class ProvInfraProjectSnapshotTestCase(APITransactionTestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter_1 = Quarter.objects.create(number=1)
        self.irm_snapshot_1 = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter_1,
            date_taken=date(year=2019, month=1, day=1),
        )
        self.project_snapshot_1 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot_1,
            project=self.project,
            status="Construction"
        )

        self.quarter_2 = Quarter.objects.create(number=2)
        self.irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter_2,
            date_taken=date(year=2019, month=6, day=1)
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot_2,
            project=self.project,
            status="Completed"
        )

    def test_latest_status_in_the_content(self):
        url = self.project.get_absolute_url()
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, '"status": "Completed"')
        self.assertNotContains(response, '"status": "Construction"')

    def test_latest_in_the_same_year(self):
        latest = ProvInfraProjectSnapshot.objects.filter(project=self.project).latest()

        self.assertEqual(self.project_snapshot_2, latest)


class ProvInfraProjectSnapshotDifferentYearsTestCase(APITransactionTestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter_1 = Quarter.objects.create(number=1)

        self.irm_snapshot_1 = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter_1,
            date_taken=date(year=2019, month=1, day=1),
        )
        self.project_snapshot_1 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot_1,
            project=self.project,
        )

        self.irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter_1,
            date_taken=date(year=2020, month=1, day=1),
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot_2,
            project=self.project,
        )

    def test_latest_in_different_years(self):
        latest = ProvInfraProjectSnapshot.objects.filter(project=self.project).latest()

        self.assertEqual(self.project_snapshot_2, latest)
