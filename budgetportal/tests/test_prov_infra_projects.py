import os
from datetime import date, timedelta

from django.core.files import File
from django.test import TransactionTestCase

from budgetportal.models import (
    FinancialYear,
    IRMSnapshot,
    ProvInfraProject,
    ProvInfraProjectSnapshot,
    Quarter,
)
from budgetportal.search_indexes import ProvInfraProjectIndex
from budgetportal.tests.helpers import BaseSeleniumTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITransactionTestCase

USERNAME = "testuser"
EMAIL = "testuser@domain.com"
PASSWORD = "12345"


class ProvInfraProjectIRMSnapshotTestCase(APITransactionTestCase):
    def setUp(self):
        file_path = os.path.abspath(
            ("budgetportal/tests/test_data/test_import_prov_infra_projects-update.xlsx")
        )
        self.file = File(open(file_path))
        self.financial_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        IRMSnapshot.objects.create(
            financial_year=self.financial_year,
            quarter=self.quarter,
            date_taken=self.date,
            file=self.file,
        )
        self.url = reverse("provincial-infrastructure-project-api-list")

    def test_import_irm_snapshot(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that 3 projects are indexed and searchable
        results = response.data["results"]
        num_of_results = len(results)
        self.assertEqual(num_of_results, 3)


class ProvInfraProjectWebflowIntegrationTestCase(BaseSeleniumTestCase):
    def setUp(self):
        self.url = reverse("provincial-infra-project-list")
        super(ProvInfraProjectWebflowIntegrationTestCase, self).setUp()
        self.timeout = 10
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=3)
        self.date = date(2050, 1, 1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter,
            date_taken=self.date,
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
        province = "Eastern Cape"
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
        self.assertEqual(filtered_num_of_projects, 5)


class ProvInfraProjectAPIDepartmentTestCase(APITransactionTestCase):
    def setUp(self):
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.facet_url = reverse("provincial-infrastructure-project-api-facets")
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=self.quarter, date_taken=self.date,
        )
        self.project_1 = ProvInfraProject.objects.create(IRM_project_id=1)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            department="Department 1",
            province="Eastern Cape",
            estimated_completion_date=self.date,
        )
        self.project_2 = ProvInfraProject.objects.create(IRM_project_id=2)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            department="Department 1",
            province="Free State",
            estimated_completion_date=self.date,
        )
        self.project_3 = ProvInfraProject.objects.create(IRM_project_id=3)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_3,
            department="Department 2",
            province="Eastern Cape",
            estimated_completion_date=self.date,
        )
        ProvInfraProjectIndex().reindex()

    def tearDown(self):
        ProvInfraProjectIndex().clear()

    def test_filter_by_department(self):
        department = "Department 1"
        data = {"department": department}

        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = response.data["count"]
        self.assertEqual(number_of_projects, 2)

    def test_facet_filter_by_department(self):
        department = "Department 1"
        province = "Eastern Cape"

        response = self.client.get(self.facet_url)
        province_facets = response.data["fields"]["province"]
        provinces_before_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                provinces_before_filtering = value["count"]

        self.assertEqual(provinces_before_filtering, 2)

        data = {"selected_facets": "department_exact:{0}".format(department)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        province_facets = response.data["fields"]["province"]
        provinces_after_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                provinces_after_filtering = value["count"]

        self.assertEqual(provinces_after_filtering, 1)


class ProvInfraProjectAPIProvinceTestCase(APITransactionTestCase):
    def setUp(self):
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.facet_url = reverse("provincial-infrastructure-project-api-facets")
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=self.quarter, date_taken=self.date,
        )
        self.project_1 = ProvInfraProject.objects.create(IRM_project_id=1)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            department="Department 1",
            province="Eastern Cape",
            estimated_completion_date=self.date,
        )
        self.project_2 = ProvInfraProject.objects.create(IRM_project_id=2)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            department="Department 1",
            province="Free State",
            estimated_completion_date=self.date,
        )
        self.project_3 = ProvInfraProject.objects.create(IRM_project_id=3)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_3,
            department="Department 2",
            province="Eastern Cape",
            estimated_completion_date=self.date,
        )
        ProvInfraProjectIndex().reindex()

    def tearDown(self):
        ProvInfraProjectIndex().clear()

    def test_filter_by_province(self):
        province = "Eastern Cape"
        data = {"province": province}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = response.data["count"]
        self.assertEqual(number_of_projects, 2)

    def test_facet_filter_by_province(self):
        province = "Eastern Cape"
        department = "Department 1"

        response = self.client.get(self.facet_url)
        department_facets = response.data["fields"]["department"]
        departments_before_filtering = 0
        for value in department_facets:
            if department == value["text"]:
                departments_before_filtering = value["count"]
        self.assertEqual(departments_before_filtering, 2)

        data = {"selected_facets": "province_exact:{0}".format(province)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        department_facets = response.data["fields"]["department"]
        departments_after_filtering = 0
        for value in department_facets:
            if department == value["text"]:
                departments_after_filtering = value["count"]
        self.assertEqual(departments_after_filtering, 1)

    def test_search_by_province(self):
        province = "Eastern Cape"
        data = {"q": province}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        num_of_projects = response.data["count"]
        self.assertEqual(num_of_projects, 2)

    def test_facet_search_by_province(self):
        province = "Eastern Cape"
        department = "Department 1"

        response = self.client.get(self.facet_url)
        department_facets = response.data["fields"]["department"]
        departments_before_filtering = 0
        for value in department_facets:
            if department == value["text"]:
                departments_before_filtering = value["count"]
        self.assertEqual(departments_before_filtering, 2)

        data = {"q": province}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        department_facets = response.data["fields"]["department"]
        departments_after_filtering = 0
        for value in department_facets:
            if department == value["text"]:
                departments_after_filtering = value["count"]
        self.assertEqual(departments_after_filtering, 1)


class ProvInfraProjectAPIStatusTestCase(APITransactionTestCase):
    def setUp(self):
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.facet_url = reverse("provincial-infrastructure-project-api-facets")
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=self.quarter, date_taken=self.date,
        )
        self.project_1 = ProvInfraProject.objects.create(IRM_project_id=1)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            province="Eastern Cape",
            status="Construction",
            estimated_completion_date=self.date,
        )
        self.project_2 = ProvInfraProject.objects.create(IRM_project_id=2)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            province="Free State",
            status="Construction",
            estimated_completion_date=self.date,
        )
        self.project_3 = ProvInfraProject.objects.create(IRM_project_id=3)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_3,
            province="Eastern Cape",
            status="Completed",
            estimated_completion_date=self.date,
        )
        ProvInfraProjectIndex().reindex()

    def tearDown(self):
        ProvInfraProjectIndex().clear()

    def test_filter_by_status(self):
        status_ = "Construction"
        data = {"status": status_}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = response.data["count"]
        self.assertEqual(number_of_projects, 2)

    def test_facet_filter_by_status(self):
        status_ = "Construction"
        province = "Eastern Cape"

        response = self.client.get(self.facet_url)
        province_facets = response.data["fields"]["province"]
        provinces_before_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                provinces_before_filtering = value["count"]

        self.assertEqual(provinces_before_filtering, 2)

        data = {"selected_facets": "status_exact:{0}".format(status_)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        province_facets = response.data["fields"]["province"]
        provinces_after_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                provinces_after_filtering = value["count"]

        self.assertEqual(provinces_after_filtering, 1)


class ProvInfraProjectAPIFundingSourceTestCase(APITransactionTestCase):
    def setUp(self):
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.facet_url = reverse("provincial-infrastructure-project-api-facets")
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=self.quarter, date_taken=self.date,
        )
        self.project_1 = ProvInfraProject.objects.create(IRM_project_id=1)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            province="Eastern Cape",
            primary_funding_source="Community Library Service Grant",
            estimated_completion_date=self.date,
        )
        self.project_2 = ProvInfraProject.objects.create(IRM_project_id=2)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            province="Free State",
            primary_funding_source="Community Library Service Grant",
            estimated_completion_date=self.date,
        )
        self.project_3 = ProvInfraProject.objects.create(IRM_project_id=3)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_3,
            province="Eastern Cape",
            primary_funding_source="Equitable Share",
            estimated_completion_date=self.date,
        )
        ProvInfraProjectIndex().reindex()

    def tearDown(self):
        ProvInfraProjectIndex().clear()

    def test_filter_by_funding_source(self):
        source = "Community Library Service Grant"
        data = {"primary_funding_source": source}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_projects = response.data["count"]
        self.assertEqual(number_of_projects, 2)

    def test_facet_filter_by_funding_source(self):
        source = "Community Library Service Grant"
        province = "Eastern Cape"

        response = self.client.get(self.facet_url)
        province_facets = response.data["fields"]["province"]
        provinces_before_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                provinces_before_filtering = value["count"]

        self.assertEqual(provinces_before_filtering, 2)

        data = {"selected_facets": "primary_funding_source_exact:{0}".format(source)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        province_facets = response.data["fields"]["province"]
        provinces_after_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                provinces_after_filtering = value["count"]

        self.assertEqual(provinces_after_filtering, 1)


class ProvInfraProjectAPIProjectNameTestCase(APITransactionTestCase):
    def setUp(self):
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.facet_url = reverse("provincial-infrastructure-project-api-facets")
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=self.quarter, date_taken=self.date,
        )
        self.project_1 = ProvInfraProject.objects.create(IRM_project_id=1)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            name="Project 1",
            estimated_completion_date=self.date,
        )
        self.project_2 = ProvInfraProject.objects.create(IRM_project_id=2)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            name="Project 2",
            estimated_completion_date=self.date,
        )
        ProvInfraProjectIndex().reindex()

    def tearDown(self):
        ProvInfraProjectIndex().clear()

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


class ProvInfraProjectAPIMunicipalityTestCase(APITransactionTestCase):
    def setUp(self):
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.facet_url = reverse("provincial-infrastructure-project-api-facets")
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=self.quarter, date_taken=self.date,
        )
        self.project_1 = ProvInfraProject.objects.create(IRM_project_id=1)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            name="Project 1",
            local_municipality="Local 1",
            estimated_completion_date=self.date,
        )
        self.project_2 = ProvInfraProject.objects.create(IRM_project_id=2)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            name="Project 2",
            local_municipality="Local 2",
            estimated_completion_date=self.date,
        )
        ProvInfraProjectIndex().reindex()

    def tearDown(self):
        ProvInfraProjectIndex().clear()

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
        name = "Project 1"
        municipality = "Local 1"
        data = {"q": municipality}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["objects"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], name)


class ProvInfraProjectAPIContractorTestCase(APITransactionTestCase):
    def setUp(self):
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.facet_url = reverse("provincial-infrastructure-project-api-facets")
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=self.quarter, date_taken=self.date,
        )
        self.project_1 = ProvInfraProject.objects.create(IRM_project_id=1)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            name="Project 1",
            main_contractor="Contractor 1",
            estimated_completion_date=self.date,
        )
        self.project_2 = ProvInfraProject.objects.create(IRM_project_id=2)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            name="Project 2",
            main_contractor="Contractor 2",
            estimated_completion_date=self.date,
        )
        ProvInfraProjectIndex().reindex()

    def tearDown(self):
        ProvInfraProjectIndex().clear()

    def test_search_by_contractor(self):
        name = "Project 1"
        contractor = "Contractor 1"
        data = {"q": contractor}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], name)

    def test_facet_search_by_contractor(self):
        name = "Project 1"
        contractor = "Contractor 1"
        data = {"q": contractor}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["objects"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], name)


class ProvInfraProjectAPISearchMultipleFieldsTestCase(APITransactionTestCase):
    def setUp(self):
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.facet_url = reverse("provincial-infrastructure-project-api-facets")
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year, quarter=self.quarter, date_taken=self.date,
        )
        self.project_1 = ProvInfraProject.objects.create(IRM_project_id=1)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            name="Something School",
            province="Eastern Cape",
            estimated_completion_date=date(year=2020, month=6, day=1),
        )
        self.project_2 = ProvInfraProject.objects.create(IRM_project_id=2)
        ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            name="Project 2",
            province="Eastern Cape",
            estimated_completion_date=date(year=2020, month=6, day=1),
        )
        ProvInfraProjectIndex().reindex()

    def tearDown(self):
        ProvInfraProjectIndex().clear()

    def test_search_multiple_fields(self):
        data = {"q": "Eastern Cape School"}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["province"], "Eastern Cape")
        self.assertEqual(results[0]["name"], "Something School")

    def test_facet_search_multiple_fields(self):
        data = {"q": "Eastern Cape School"}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["objects"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["province"], "Eastern Cape")
        self.assertEqual(results[0]["name"], "Something School")


class ProvInfraProjectAPIURLPathTestCase(APITransactionTestCase):
    def setUp(self):
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter,
            date_taken=self.date,
        )
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.facet_url = reverse("provincial-infrastructure-project-api-facets")
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        ProvInfraProjectSnapshot.objects.create(
                irm_snapshot=self.irm_snapshot,
                project=self.project,
                name="Project 1",
                estimated_completion_date=date(year=2020, month=1, day=1),
            )

        ProvInfraProjectIndex().reindex()

    def tearDown(self):
        ProvInfraProjectIndex().clear()

    def test_url_path(self):
        name = "Project 1"
        data = {"name": name}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["results"][0]
        url_path = result["url_path"]

        response = self.client.get(url_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, name)

    def test_facet_url_path(self):
        name = "Project 1"
        data = {"q": name}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["objects"]["results"][0]
        url_path = result["url_path"]
        response = self.client.get(url_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, name)


class ProvInfraProjectSnapshotTestCase(APITransactionTestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter_1 = Quarter.objects.create(number=1)
        self.date_1 = date(year=2050, month=1, day=1)
        self.date_2 = date(year=2070, month=1, day=1)
        self.irm_snapshot_1 = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter_1,
            date_taken=self.date_1,
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
            date_taken=self.date_2,
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
        latest = self.project.project_snapshots.latest()

        self.assertEqual(self.project_snapshot_2, latest)


class ProvInfraProjectSnapshotDifferentYearsTestCase(APITransactionTestCase):
    def setUp(self):
        self.project = ProvInfraProject.objects.create(IRM_project_id=1)
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter_1 = Quarter.objects.create(number=1)
        self.date_1 = date(year=2050, month=1, day=1)
        self.date_2 = date(year=2070, month=1, day=1)
        self.irm_snapshot_1 = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter_1,
            date_taken=self.date_1,
        )
        self.project_snapshot_1 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot_1, project=self.project,
        )

        self.irm_snapshot_2 = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter_1,
            date_taken=self.date_2,
        )
        self.project_snapshot_2 = ProvInfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot_2, project=self.project,
        )

    def test_latest_in_different_years(self):
        latest = self.project.project_snapshots.latest()

        self.assertEqual(self.project_snapshot_2, latest)


class ProvInfraProjectFullTextSearchTestCase(APITransactionTestCase):
    def setUp(self):
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
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


class ProvInfraProjectDetailPageTestCase(TransactionTestCase):
    def setUp(self):
        self.fin_year = FinancialYear.objects.create(slug="2050-51")
        self.quarter = Quarter.objects.create(number=3)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            financial_year=self.fin_year,
            quarter=self.quarter,
            date_taken=self.date,
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
