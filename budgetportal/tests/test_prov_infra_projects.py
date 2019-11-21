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
from budgetportal.search_indexes import ProvInfraProjectIndex
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
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter,
            date_taken=date(year=2019, month=1, day=1),
        )
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.facet_url = reverse("provincial-infrastructure-project-api-facets")
        self.provinces = ["Eastern Cape", "Free State"]
        self.statuses = ["Design", "Construction"]
        self.sources = [
            "Education Infrastructure Grant",
            "Community Library Service Grant",
        ]

        for i in range(30):
            if i < 15:
                status_ = self.statuses[0]
                province = self.provinces[0]
                source = self.sources[0]
            else:
                status_ = self.statuses[1]
                province = self.provinces[1]
                source = self.sources[1]
            project = ProvInfraProject.objects.create(IRM_project_id=i)
            ProvInfraProjectSnapshot.objects.create(
                irm_snapshot=self.irm_snapshot,
                project=project,
                name="Project {}".format(i),
                department="Department {}".format(i),
                local_municipality="Local {}".format(i),
                district_municipality="District {}".format(i),
                province=province,
                status=status_,
                primary_funding_source=source,
                main_contractor="Contractor {}".format(i),
                principle_agent="Principle Agent {}".format(i),
                program_implementing_agent="Program Agent {}".format(i),
                other_parties="Service Provider: XXXX{}".format(i),
                estimated_completion_date=date(year=2020, month=1, day=1),
            )

        ProvInfraProjectIndex().reindex()

    def tearDown(self):
        ProvInfraProjectIndex().clear()

    def test_filter_by_department(self):
        department = "Department 1"
        project = ProvInfraProjectSnapshot.objects.get(department=department)

        data = {"department": department}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = len(response.data["results"])
        response_data = response.data["results"][0]
        self.assertEqual(number_of_projects, 1)
        self.assertEqual(response_data["name"], project.name)

    def test_facet_filter_by_department(self):
        department = "Test Department"
        for i in range(1, 6):
            date_ = date(year=2019, month=1, day=i * 5)
            irm_snapshot = IRMSnapshot.objects.create(
                financial_year=self.fin_year, quarter=self.quarter, date_taken=date_,
            )
            project = ProvInfraProject.objects.get(IRM_project_id=i)
            ProvInfraProjectSnapshot.objects.create(
                irm_snapshot=irm_snapshot,
                project=project,
                department=department,
                estimated_completion_date=date_,
            )
        ProvInfraProjectIndex().update()

        data = {"selected_facets": "department_exact:{0}".format(department)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        num_of_departments = response.data["objects"]["count"]
        self.assertEqual(num_of_departments, 5)

    def test_filter_by_province(self):
        province = "Eastern Cape"
        data = {"province": province}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = len(response.data["results"])
        self.assertEqual(number_of_projects, 15)

    def test_facet_filter_by_province(self):
        province = "Eastern Cape"

        data = {"selected_facets": "province_exact:{0}".format(province)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        objects = response.data["objects"]
        num_of_provinces = objects["count"]
        self.assertEqual(num_of_provinces, 15)

    def test_filter_by_status(self):
        status_ = "Construction"
        data = {"status": status_}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = len(response.data["results"])
        self.assertEqual(number_of_projects, 15)

    def test_facet_filter_by_status(self):
        status_ = "Construction"
        data = {"selected_facets": "status_exact:{0}".format(status_)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        objects = response.data["objects"]
        num_of_statuses = objects["count"]
        self.assertEqual(num_of_statuses, 15)

    def test_filter_by_funding_source(self):
        source = "Community Library Service Grant"
        data = {"primary_funding_source": source}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = len(response.data["results"])
        self.assertEqual(number_of_projects, 15)

    def test_facet_filter_by_funding_source(self):
        source = "Community Library Service Grant"
        data = {"selected_facets": "primary_funding_source_exact:{0}".format(source)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        objects = response.data["objects"]
        num_of_statuses = objects["count"]
        self.assertEqual(num_of_statuses, 15)

    def test_search_by_project_name(self):
        name = "Project 1"
        data = {"name": name}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], name)

    def test_search_by_municipality(self):
        # TODO : not working yet
        municipality = "Local 1"
        data = {"local_municipality": municipality}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["local_municipality"], municipality)

    def test_search_by_province(self):
        province = "Eastern Cape"
        data = {"province": province}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 15)
        self.assertEqual(results[0]["province"], province)

    def test_search_by_contractor(self):
        # TODO: not working yet
        contractor = "Contractor 3"
        data = {"main_contractor": contractor}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, contractor)

    def test_search_multiple_fields(self):
        project = ProvInfraProject.objects.create(IRM_project_id=123456789)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=project,
            name="Something School",
            province="Eastern Cape",
            estimated_completion_date=date(year=2020, month=6, day=1),
        )
        ProvInfraProjectIndex().update()

        data = {"q": "Eastern Cape School"}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]

        # There should be only one match because first 30 objects don't
        # have school word
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["province"], "Eastern Cape")
        self.assertEqual(results[0]["name"], "Something School")

    def test_facet_search_multiple_fields(self):
        project = ProvInfraProject.objects.create(IRM_project_id=123456789)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=project,
            name="Something School",
            province="Eastern Cape",
            estimated_completion_date=date(year=2020, month=6, day=1),
        )
        ProvInfraProjectIndex().update()

        data = {"q": "Eastern Cape School"}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["objects"]["results"]

        # There should be only one match because first 30 objects don't
        # have school word
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["province"], "Eastern Cape")
        self.assertEqual(results[0]["name"], "Something School")

    def test_url_path(self):
        name = "Project 10"
        data = {"name": name}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["results"][0]
        url_path = result["url_path"]

        response = self.client.get(url_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, name)

    def test_facet_url_path(self):
        province = "Eastern Cape"
        data = {"selected_facets": "province_exact:{0}".format(province)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["objects"]["results"][0]
        url_path = result["url_path"]
        response = self.client.get(url_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, province)


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
            status="Construction",
        )

        self.quarter_2 = Quarter.objects.create(number=2)
        self.irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter_2,
            date_taken=date(year=2019, month=6, day=1),
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot_2, project=self.project, status="Completed"
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
            irm_snapshot=self.irm_snapshot_1, project=self.project,
        )

        self.irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter_1,
            date_taken=date(year=2020, month=1, day=1),
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot_2, project=self.project,
        )

    def test_latest_in_different_years(self):
        latest = ProvInfraProjectSnapshot.objects.filter(project=self.project).latest()

        self.assertEqual(self.project_snapshot_2, latest)
