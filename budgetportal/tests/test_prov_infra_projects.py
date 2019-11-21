import os
from datetime import date, timedelta

from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from allauth.account.models import EmailAddress
from budgetportal.models import (
    FinancialYear,
    IRMSnapshot,
    ProvInfraProject,
    ProvInfraProjectSnapshot,
    Quarter,
)
from budgetportal.search_indexes import ProvInfraProjectIndex
from budgetportal.tests.helpers import BaseSeleniumTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITransactionTestCase

USERNAME = "testuser"
EMAIL = "testuser@domain.com"
PASSWORD = "12345"


class ProvInfraProjectSeleniumIRMSnapshotTestCase(BaseSeleniumTestCase):
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
        self.timeout = 60
        self.search_url = "/infrastructure-projects/provincial/"
        super(ProvInfraProjectSeleniumIRMSnapshotTestCase, self).setUp()

    def test_import_irm_snapshot(self):
        # TODO: not completed yet
        filename = (
            "budgetportal/tests/test_data/test_import_prov_infra_projects-update.xlsx"
        )

        selenium = self.selenium

        # Login
        selenium.get("%s%s" % (self.live_server_url, "/admin/"))
        username = selenium.find_element_by_id("id_login")
        password = selenium.find_element_by_id("id_password")
        submit_button = selenium.find_element_by_css_selector('button[type="submit"]')
        username.send_keys(EMAIL)
        password.send_keys(PASSWORD)
        submit_button.click()

        # Navigate to form
        selenium.find_element_by_link_text("IRM Snapshots").click()
        selenium.find_element_by_link_text("ADD IRM SNAPSHOT").click()

        # Select dropdown menus and "browse" button
        financial_year_select = Select(selenium.find_element_by_id("id_financial_year"))
        quarter_select = Select(selenium.find_element_by_id("id_quarter"))
        file_import = selenium.find_element_by_id("id_file")

        # Fill the form
        selenium.find_element_by_link_text("Today").click()
        selenium.find_element_by_link_text("Now").click()
        financial_year_select.select_by_value(str(self.financial_year.id))
        quarter_select.select_by_value(str(self.quarter.id))
        file_import.send_keys(os.path.abspath(filename))

        # Save the form and wait until success
        selenium.find_element_by_css_selector('input[value="Save"]').click()
        try:
            success = WebDriverWait(selenium, self.timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "success"))
            )
        except TimeoutException:
            self.fail("Loading took too much time!")
        # Get search url
        selenium.get("%s%s" % (self.live_server_url, self.search_url))
        num_of_projects = selenium.find_element_by_xpath(
            '//*[@id="num-matching-projects-field"]'
        ).text
        self.assertEqual(num_of_projects, 11)


class ProvInfraProjectWebflowIntegrationTestCase(BaseSeleniumTestCase):
    def setUp(self):
        self.url = reverse("provincial-infra-project-list")
        super(ProvInfraProjectWebflowIntegrationTestCase, self).setUp()
        self.timeout = 10
        self.fin_year = FinancialYear.objects.create(slug="2050-51")
        self.quarter = Quarter.objects.create(number=3)
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter,
            date_taken=date(year=2019, month=1, day=1),
        )
        self.project = ProvInfraProject.objects.create(IRM_project_id=123456)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project,
            name="Project 123456",
            department="Health",
            province="Western Cape",
            status="Construction",
            primary_funding_source="Health Infrastructure Grant",
            estimated_completion_date=date(year=2020, month=1, day=1),
        )
        # Add ten projects
        provinces = ["Eastern Cape", "Free State"]
        for i in range(10):
            if i < 5:
                province = provinces[0]
            else:
                province = provinces[1]
            project = ProvInfraProject.objects.create(IRM_project_id=i)
            ProvInfraProjectSnapshot.objects.create(
                irm_snapshot=self.irm_snapshot,
                project=project,
                name="Project {}".format(i),
                province=province,
                estimated_completion_date=date(year=2020, month=1, day=1),
            )
        ProvInfraProjectIndex().reindex()

    def tearDown(self):
        ProvInfraProjectIndex().clear()

    def test_correct_numbers_showed(self):
        selenium = self.selenium
        selenium.get("%s%s" % (self.live_server_url, self.url))
        num_of_projects = selenium.find_element_by_xpath(
            '//*[@id="num-matching-projects-field"]'
        ).text
        num_of_projects = int(num_of_projects)
        self.assertEqual(num_of_projects, 11)

        num_of_items = len(
            selenium.find_elements_by_xpath('//*[@id="result-list-container"]/a')
        )
        # Header is also counted
        num_of_items = num_of_items - 1
        self.assertEqual(num_of_projects, num_of_items)

    def test_number_updated_after_search(self):
        # TODO: Not working yet
        province = "Project 1"
        selenium = self.selenium
        selenium.get("%s%s" % (self.live_server_url, self.url))
        num_of_projects = selenium.find_element_by_xpath(
            '//*[@id="num-matching-projects-field"]'
        ).text
        num_of_projects = int(num_of_projects)
        self.assertEqual(num_of_projects, 11)

        search_field = selenium.find_element_by_name("Infrastructure-Search")
        search_field.send_keys(province)
        selenium.implicitly_wait(self.timeout)
        search_button = selenium.find_element_by_id("Search-Button")
        search_button.click()
        selenium.implicitly_wait(self.timeout)
        selenium.refresh()
        filtered_num_of_projects = selenium.find_element_by_xpath(
            '//*[@id="num-matching-projects-field"]'
        ).text
        filtered_num_of_projects = int(filtered_num_of_projects)
        # self.assertEqual(filtered_num_of_projects, 5)


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
        # Add 5 projects with Test Department
        department = "Test Department"
        for i in range(100, 106):
            if i < 103:
                province = "Eastern Cape"
            else:
                province = "Free State"
            date_ = date(year=2019, month=1, day=1) + timedelta(days=i)
            irm_snapshot = IRMSnapshot.objects.create(
                financial_year=self.fin_year, quarter=self.quarter, date_taken=date_,
            )
            project = ProvInfraProject.objects.create(IRM_project_id=i)
            ProvInfraProjectSnapshot.objects.create(
                irm_snapshot=irm_snapshot,
                project=project,
                department=department,
                province=province,
                estimated_completion_date=date_,
            )
        ProvInfraProjectIndex().update()

        province = "Eastern Cape"
        response = self.client.get(self.facet_url)
        province_facets = response.data["fields"]["province"]
        provinces_before_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                provinces_before_filtering = value["count"]

        self.assertEqual(provinces_before_filtering, 18)

        data = {"selected_facets": "department_exact:{0}".format(department)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        province_facets = response.data["fields"]["province"]
        provinces_after_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                provinces_after_filtering = value["count"]

        self.assertEqual(provinces_after_filtering, 3)
        self.assertNotEqual(provinces_before_filtering, provinces_after_filtering)

    def test_filter_by_province(self):
        province = "Eastern Cape"
        data = {"province": province}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = len(response.data["results"])
        self.assertEqual(number_of_projects, 15)

    def test_facet_filter_by_province(self):
        department = "Department 1"
        project = ProvInfraProject.objects.create(IRM_project_id=123456)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=project,
            department=department,
            province="Western Cape",
            estimated_completion_date=date(year=2029, month=1, day=30),
        )
        ProvInfraProjectIndex().update()

        response = self.client.get(self.facet_url)
        department_facets = response.data["fields"]["department"]
        departments_before_filtering = 0
        for value in department_facets:
            if department == value["text"]:
                departments_before_filtering = value["count"]
        self.assertEqual(departments_before_filtering, 2)

        province = "Eastern Cape"
        data = {"selected_facets": "province_exact:{0}".format(province)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        department_facets = response.data["fields"]["department"]
        departments_after_filtering = 0
        for value in department_facets:
            if department == value["text"]:
                departments_after_filtering = value["count"]
        self.assertEqual(departments_after_filtering, 1)

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

        status_facets = response.data["fields"]["status"]
        num_of_statuses = 0
        for value in status_facets:
            if status_ == value["text"]:
                num_of_statuses = value["count"]
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

        source_facets = response.data["fields"]["primary_funding_source"]
        num_of_sources = 0
        for value in source_facets:
            if source == value["text"]:
                num_of_sources = value["count"]
        self.assertEqual(num_of_sources, 15)

    def test_search_by_project_name(self):
        name = "Project 1"
        data = {"q": name}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], name)

    def test_facet_search_by_project_name(self):
        name = "Project 1"
        data = {"q": name}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["objects"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], name)

    def test_search_by_municipality(self):
        name = "Project 1"
        municipality = "Local 1"
        data = {"q": municipality}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], name)

    def test_facet_search_by_municipality(self):
        municipality = "Local 1"
        data = {"q": municipality}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["objects"]["results"]
        self.assertEqual(len(results), 1)

        province = "Eastern Cape"
        data = {"selected_facets": "province_exact:{0}".format(province)}
        response = self.client.get(self.facet_url, data)
        province_results = response.data["objects"]["results"]
        self.assertNotEqual(results, province_results)

    def test_search_by_province(self):
        province = "Eastern Cape"
        data = {"q": province}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 15)

    def test_facet_search_by_province(self):
        province = "Eastern Cape"
        data = {"selected_facets": "province_exact:{0}".format(province)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        province_results = response.data["objects"]["count"]
        self.assertEqual(province_results, 15)

    def test_search_by_contractor(self):
        name = "Project 3"
        contractor = "Contractor 3"
        data = {"q": contractor}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], name)

    def test_facet_search_by_contractor(self):
        contractor = "Contractor 3"
        data = {"q": contractor}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["objects"]["count"]
        self.assertNotEqual(results, 0)

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


class ProvInfraProjectFullTextSearchTestCase(APITransactionTestCase):
    def setUp(self):
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2019, month=1, day=1)
        self.project_1 = ProvInfraProject.objects.create(IRM_project_id=1)

        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=self.quarter, date_taken=self.date,
        )
        self.project_snapshot_1 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            name="Blue School",
            province="Eastern Cape",
            estimated_completion_date=self.date,
        )

        self.project_2 = ProvInfraProject.objects.create(IRM_project_id=2)
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            name="Red School",
            province="Limpopo",
            estimated_completion_date=self.date,
        )
        ProvInfraProjectIndex().reindex()

    def tearDown(self):
        ProvInfraProjectIndex().clear()

    def test_correct_project_returned(self):
        search = "Eastern Cape School"
        data = {"q": search}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Blue School")
        self.assertNotContains(response, "Red School")


class ProvInfraProjectDetailPageTestCase(APITransactionTestCase):
    def setUp(self):
        self.fin_year = FinancialYear.objects.create(slug="2050-51")
        self.quarter = Quarter.objects.create(number=3)
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter,
            date_taken=date(year=2019, month=1, day=1),
        )
        self.project = ProvInfraProject.objects.create(IRM_project_id=123456)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project,
            name="Project 123456",
            department="Health",
            province="Eastern Cape",
            status="Construction",
            primary_funding_source="Health Infrastructure Grant",
            estimated_completion_date=date(year=2020, month=1, day=1),
        )

        ProvInfraProjectIndex().reindex()

    def tearDown(self):
        ProvInfraProjectIndex().clear()

    def test_project_detail_page_fields(self):
        url = self.project.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            "<title>Project 123456, Eastern Cape Infrastructure projects - vulekamali</title>",
        )
        self.assertContains(
            response,
            '"Provincial infrastructure project by the Eastern Cape Health department."',
        )
        self.assertContains(response, '"name": "Project 123456"')
        self.assertContains(response, '"department": "Health"')
        self.assertContains(response, '"province": "Eastern Cape"')
        self.assertContains(response, '"status": "Construction"')
        self.assertContains(
            response, '"primary_funding_source": "Health Infrastructure Grant"'
        )
