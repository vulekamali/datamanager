#!/usr/bin/python
# -*- coding: utf-8 -*
import os
import io
import csv
from datetime import date, datetime
from budgetportal.models import (
    FinancialYear,
    Sphere,
    IRMSnapshot,
    InfraProject,
    InfraProjectSnapshot,
    Quarter,
)
from budgetportal.search_indexes import InfraProjectIndex
from budgetportal.tests.helpers import BaseSeleniumTestCase
from django.conf import settings
from django.core.files import File
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from budgetportal.infra_projects import irm_preprocessor
from budgetportal.webflow.serializers import InfraProjectCSVSerializer
from tablib import Dataset
from django.test import TransactionTestCase
from budgetportal.infra_projects import InfraProjectSnapshotResource
from budgetportal.tests.helpers import WagtailHackMixin
from budgetportal.tasks import format_error

EMPTY_FILE_PATH = os.path.abspath(
    "budgetportal/tests/test_data/test_prov_infra_projects_empty_file.xlsx"
)


class InfraProjectIRMSnapshotTestCase(APITestCase):
    """
    End-to-end test: Uploading a file changes state from nothing in search
    results to the right projects in search results.
    """

    def setUp(self):
        InfraProjectIndex().clear()
        file_path = os.path.abspath(
            ("budgetportal/tests/test_data/test_import_prov_infra_projects-update.xlsx")
        )
        self.file = File(open(file_path, "rb"))
        financial_year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(
            financial_year=financial_year, name="Provincial"
        )
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.url = reverse("infrastructure-project-api-list")

    def tearDown(self):
        self.file.close()

    def test_import_irm_snapshot(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that there is no project at the beginning
        results = response.data["results"]
        num_of_results = len(results)
        self.assertEqual(num_of_results, 0)
        self.assertEqual(
            response.data["csv_download_url"],
            "/infrastructure-projects/full/search/csv",
        )

        IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=self.file,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that 3 projects are indexed and searchable
        results = response.data["results"]
        num_of_results = len(results)
        self.assertEqual(num_of_results, 3)
        self.assertEqual(
            response.data["csv_download_url"],
            "/infrastructure-projects/full/search/csv",
        )


class NatProvSameIRMIDInfraProjectIRMSnapshotTestCase(
    WagtailHackMixin, TransactionTestCase
):
    """
    Test that importing a national and provincial project with the same
    IRM ID yields different project instances with different URLs
    """

    def setUp(self):
        financial_year = FinancialYear.objects.create(slug="2030-31")
        self.prov_sphere = Sphere.objects.create(
            financial_year=financial_year, name="Provincial"
        )
        self.nat_sphere = Sphere.objects.create(
            financial_year=financial_year, name="National"
        )
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        prov_IRM_snapshot = IRMSnapshot.objects.create(
            sphere=self.prov_sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(open(EMPTY_FILE_PATH, "rb")),
        )
        nat_IRM_snapshot = IRMSnapshot.objects.create(
            sphere=self.nat_sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(open(EMPTY_FILE_PATH, "rb")),
        )
        headers = irm_preprocessor.OUTPUT_HEADERS + ["irm_snapshot", "sphere_slug"]
        self.prov_dataset = Dataset(headers=headers)
        self.nat_dataset = Dataset(headers=headers)
        num_columns = len(irm_preprocessor.OUTPUT_HEADERS)
        prov_row = (
            [12345, "proj-1", "A Prov Project"]
            + [None] * (num_columns - 3)
            + [prov_IRM_snapshot.id, "provincial"]
        )
        self.prov_dataset.append(prov_row)
        nat_row = (
            [12345, "PROJ-1", "A Nat Project"]
            + [None] * (num_columns - 3)
            + [nat_IRM_snapshot.id, "national"]
        )
        self.nat_dataset.append(nat_row)
        InfraProject.objects.create(IRM_project_id=12345, sphere_slug="national")
        InfraProject.objects.create(IRM_project_id=12345, sphere_slug="provincial")

    def test(self):
        self.assertEqual(2, InfraProject.objects.count())

        resource = InfraProjectSnapshotResource()
        prov_result = resource.import_data(self.prov_dataset)
        for row_num, row_result in enumerate(prov_result.rows):
            if row_result.errors:
                print("\n".join([format_error(e) for e in row_result.errors]))

        nat_result = resource.import_data(self.nat_dataset)
        for row_num, row_result in enumerate(nat_result.rows):
            if row_result.errors:
                print("\n".join([format_error(e) for e in row_result.errors]))

        nat_project = InfraProject.objects.get(sphere_slug="national")
        prov_project = InfraProject.objects.get(sphere_slug="provincial")
        self.assertEqual(12345, nat_project.IRM_project_id)
        self.assertEqual(12345, prov_project.IRM_project_id)
        self.assertNotEqual(nat_project.id, prov_project.id)
        self.assertEqual("A Nat Project", nat_project.project_snapshots.latest().name)
        self.assertEqual("A Prov Project", prov_project.project_snapshots.latest().name)


class InfraProjectDetailPageTestCase(BaseSeleniumTestCase):
    def setUp(self):
        super(InfraProjectDetailPageTestCase, self).setUp()
        InfraProjectIndex().clear()
        self.file = open(EMPTY_FILE_PATH, "rb")
        fin_year = FinancialYear.objects.create(slug="2050-51", published=True)
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        self.quarter = Quarter.objects.create(number=3)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(self.file),
        )
        self.project = InfraProject.objects.create(IRM_project_id=123456)
        self.project_snapshot = InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project,
            name="BLUE JUNIOR SECONDARY SCHOOL",
            # Administration
            department="Education",
            budget_programme="Programme 2 - Public Ordinary School Education",
            project_number="W/50042423/WS",
            status="Construction",
            # Location
            province="KwaZulu-Natal",
            local_municipality="Dr Nkosazana Dlamini Zuma",
            district_municipality="Harry Gwala",
            # Implementation
            program_implementing_agent="DOPW",
            principle_agent="PRINCIPLE AGENT",
            main_contractor="MAIN CONTRACTOR",
            other_parties="OTHERS",
            # Funding
            primary_funding_source="Education Infrastructure Grant",
            nature_of_investment="Upgrading and Additions",
            funding_status="Tabled",
            # Budget
            estimated_total_project_cost=680000,
            total_construction_costs=562000,
            total_professional_fees=118000,
            # Cost to date
            expenditure_from_previous_years_total=556479,
            expenditure_from_previous_years_professional_fees=118000,
            expenditure_from_previous_years_construction_costs=0,
            variation_orders=0,
            # Original Budget FY
            main_appropriation_total=337000,
            main_appropriation_construction_costs=276000,
            main_appropriation_professional_fees=61000,
            # Adjustment Budget FY
            adjusted_appropriation_total=1,
            adjusted_appropriation_construction_costs=2,
            adjusted_appropriation_professional_fees=3,
            # Overall timeline
            start_date=date(2016, 6, 13),
            estimated_completion_date=date(year=2021, month=6, day=30),
            # Construction timeline
            estimated_construction_start_date=date(2017, 2, 1),
            estimated_construction_end_date=date(2020, 12, 31),
            contracted_construction_end_date=date(2021, 1, 1),
        )

        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file.close()

    def test_project_detail_page_fields(self):
        url = self.project.get_absolute_url()
        self.selenium.get("%s%s" % (self.live_server_url, url))
        selenium = self.selenium
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".page-heading"), u"BLUE JUNIOR SECONDARY SCHOOL"
            )
        )
        title = selenium.find_element_by_css_selector(".page-heading").text
        self.assertEqual(title, u"BLUE JUNIOR SECONDARY SCHOOL")

        source = selenium.find_element_by_css_selector(
            ".primary-funding-source-field"
        ).text
        investment = selenium.find_element_by_css_selector(
            ".nature-of-investment-field"
        ).text
        funding_status = selenium.find_element_by_css_selector(
            ".funding-status-field"
        ).text
        csv_download_url = selenium.find_element_by_css_selector(
            ".header__download"
        ).get_attribute("href")

        self.assertEqual(source, u"Education Infrastructure Grant")
        self.assertEqual(investment, u"Upgrading and Additions")
        self.assertEqual(funding_status, u"Tabled")
        self.assertIn(self.project.csv_download_url, csv_download_url)

        department = selenium.find_element_by_css_selector(".department-field").text
        budget_programme = selenium.find_element_by_css_selector(
            ".budget-programme-field"
        ).text
        project_status = selenium.find_element_by_css_selector(".status-field").text
        project_number = selenium.find_element_by_css_selector(
            ".project-number-field"
        ).text

        self.assertEqual(department, u"Education")
        self.assertEqual(
            budget_programme, u"Programme 2 - Public Ordinary School Education"
        )
        self.assertEqual(project_status, u"Construction")
        self.assertEqual(project_number, u"W/50042423/WS")

        province = selenium.find_element_by_css_selector(".province-field").text
        local_muni = selenium.find_element_by_css_selector(
            "#local-municipality-field"
        ).text
        district_muni = selenium.find_element_by_css_selector(
            "#district-municipality-field"
        ).text
        gps_location = selenium.find_element_by_css_selector(".coordinates-field").text

        self.assertEqual(province, u"KwaZulu-Natal")
        self.assertEqual(local_muni, u"Dr Nkosazana Dlamini Zuma")
        self.assertEqual(district_muni, u"Harry Gwala")
        self.assertEqual(gps_location, u"Not available")

        implementing_agent = selenium.find_element_by_css_selector(
            ".program-implementing-agent-field"
        ).text
        principle_agent = selenium.find_element_by_css_selector(
            ".principle-agent-field"
        ).text
        main_contractor = selenium.find_element_by_css_selector(
            ".main-contractor-field"
        ).text
        others = selenium.find_element_by_css_selector(
            ".other-service-providers-field"
        ).text

        self.assertEqual(implementing_agent, u"DOPW")
        self.assertEqual(principle_agent, u"PRINCIPLE AGENT")
        self.assertEqual(main_contractor, u"MAIN CONTRACTOR")
        self.assertEqual(others, u"OTHERS")

        professional_fees = selenium.find_element_by_css_selector(
            "#total-professional-fees-field"
        ).text

        self.wait_until_text_in("#total-construction-costs-field", u"R 562,000")
        self.assertEqual(professional_fees, u"R 118,000")

        expenditure_from_prev = selenium.find_element_by_css_selector(
            ".expenditure-from-previous-years-total-field"
        ).text
        const_cost_from_prev = selenium.find_element_by_css_selector(
            ".expenditure-from-previous-years-construction-costs-field"
        ).text
        prof_cost_from_prev = selenium.find_element_by_css_selector(
            "#expenditure-from-previous-years-professional-fees-field"
        ).text
        variation_order = selenium.find_element_by_css_selector(
            ".variation-orders-field"
        ).text

        self.assertEqual(expenditure_from_prev, u"R 556,479")
        self.assertEqual(const_cost_from_prev, u"R 0")
        self.assertEqual(prof_cost_from_prev, u"R 118,000")
        self.assertEqual(variation_order, u"R 0")

        total_main_approp = selenium.find_element_by_css_selector(
            ".main-appropriation-total-field"
        ).text
        const_cost_main_approp = selenium.find_element_by_css_selector(
            ".main-appropriation-construction-costs-field"
        ).text
        prof_fees_main_approp = selenium.find_element_by_css_selector(
            ".main-appropriation-professional-fees-field"
        ).text

        self.assertEqual(total_main_approp, u"R 337,000")
        self.assertEqual(const_cost_main_approp, u"R 276,000")
        self.assertEqual(prof_fees_main_approp, u"R 61,000")

        start_date = selenium.find_element_by_css_selector(".start-date-field").text
        estimated_completion = selenium.find_element_by_css_selector(
            ".estimated-completion-date-field"
        ).text

        self.assertEqual(start_date, u"2016-06-13")
        self.assertEqual(estimated_completion, u"2021-06-30")

        est_const_start_date = selenium.find_element_by_css_selector(
            ".estimated-construction-start-date-field"
        ).text
        contracted_const_end_date = selenium.find_element_by_css_selector(
            ".contracted-construction-end-date-field"
        ).text
        est__const_end_date = selenium.find_element_by_css_selector(
            ".estimated-construction-end-date-field"
        ).text

        self.assertEqual(est_const_start_date, u"2017-02-01")
        self.assertEqual(contracted_const_end_date, u"2021-01-01")
        self.assertEqual(est__const_end_date, u"2020-12-31")


class InfraProjectSearchPageTestCase(BaseSeleniumTestCase):
    def setUp(self):
        super(InfraProjectSearchPageTestCase, self).setUp()
        InfraProjectIndex().clear()
        self.file = open(EMPTY_FILE_PATH, "rb")
        self.url = reverse("infra-project-list")
        self.wait = WebDriverWait(self.selenium, 5)
        fin_year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        self.quarter = Quarter.objects.create(number=3)
        self.date = date(2050, 1, 1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(self.file),
        )
        self.project = InfraProject.objects.create(IRM_project_id=123456)
        InfraProjectSnapshot.objects.create(
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
            project = InfraProject.objects.create(IRM_project_id=i)
            InfraProjectSnapshot.objects.create(
                irm_snapshot=self.irm_snapshot,
                project=project,
                name="Project {}".format(i),
                province=province,
                estimated_completion_date=date(year=2020, month=1, day=1),
            )
        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file.close()

    def test_search_homepage_correct_numbers(self):
        selenium = self.selenium
        selenium.get("%s%s" % (self.live_server_url, self.url))
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#num-matching-projects-field"), u"11"
            )
        )
        num_of_projects = selenium.find_element_by_css_selector(
            "#num-matching-projects-field"
        ).text
        num_of_projects = int(num_of_projects)
        self.assertEqual(num_of_projects, 11)

        num_of_items = len(
            selenium.find_elements_by_css_selector(
                "#result-list-container .narrow-card_wrapper"
            )
        )
        self.assertEqual(num_of_projects, num_of_items)

    def test_number_updated_after_search(self):
        province = "Eastern Cape"
        selenium = self.selenium
        selenium.get("%s%s" % (self.live_server_url, self.url))
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#num-matching-projects-field"), u"11"
            )
        )
        num_of_projects = selenium.find_element_by_css_selector(
            "#num-matching-projects-field"
        ).text
        num_of_projects = int(num_of_projects)
        self.assertEqual(num_of_projects, 11)

        search_field = selenium.find_element_by_css_selector(
            "#Infrastructure-Search-Input"
        )
        search_button = selenium.find_element_by_css_selector("#Search-Button")
        search_field.send_keys(province)
        search_button.click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#num-matching-projects-field"), u"5"
            )
        )
        filtered_num_of_projects = selenium.find_element_by_css_selector(
            "#num-matching-projects-field"
        ).text
        filtered_num_of_projects = int(filtered_num_of_projects)
        self.assertEqual(filtered_num_of_projects, 5)

    def test_csv_download_button_populating(self):
        selenium = self.selenium
        selenium.get("%s%s" % (self.live_server_url, self.url))
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#num-matching-projects-field"), u"11"
            )
        )
        csv_download_url = selenium.find_element_by_css_selector(
            "#search-results-download-button"
        ).get_attribute("href")
        self.assertIn(
            "infrastructure-projects/full/search/csv?q=&ordering=status_order",
            csv_download_url,
        )


class InfraProjectAPIDepartmentTestCase(APITestCase):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file = open(EMPTY_FILE_PATH, "rb")
        self.url = reverse("infrastructure-project-api-list")
        self.facet_url = reverse("infrastructure-project-api-facets")
        fin_year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(self.file),
        )
        self.project_1 = InfraProject.objects.create(IRM_project_id=1)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            department="Department 1",
            province="Eastern Cape",
            estimated_completion_date=self.date,
        )
        self.project_2 = InfraProject.objects.create(IRM_project_id=2)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            department="Department 1",
            province="Free State",
            estimated_completion_date=self.date,
        )
        self.project_3 = InfraProject.objects.create(IRM_project_id=3)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_3,
            department="Department 2",
            province="Eastern Cape",
            estimated_completion_date=self.date,
        )
        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file.close()

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
        province_projects_before_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                province_projects_before_filtering = value["count"]

        self.assertEqual(province_projects_before_filtering, 2)

        data = {"selected_facets": "department_exact:{0}".format(department)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        province_facets = response.data["fields"]["province"]
        province_projects_after_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                province_projects_after_filtering = value["count"]

        self.assertEqual(province_projects_after_filtering, 1)


class InfraProjectAPIProvinceTestCase(APITestCase):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file = open(EMPTY_FILE_PATH, "rb")
        self.url = reverse("infrastructure-project-api-list")
        self.facet_url = reverse("infrastructure-project-api-facets")
        fin_year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(self.file),
        )
        self.project_1 = InfraProject.objects.create(IRM_project_id=1)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            department="Department 1",
            province="Eastern Cape",
            estimated_completion_date=self.date,
        )
        self.project_2 = InfraProject.objects.create(IRM_project_id=2)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            department="Department 1",
            province="Free State",
            estimated_completion_date=self.date,
        )
        self.project_3 = InfraProject.objects.create(IRM_project_id=3)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_3,
            department="Department 2",
            province="Eastern Cape",
            estimated_completion_date=self.date,
        )
        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file.close()

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
        department_projects_before_filtering = 0
        for value in department_facets:
            if department == value["text"]:
                department_projects_before_filtering = value["count"]
        self.assertEqual(department_projects_before_filtering, 2)

        data = {"selected_facets": "province_exact:{0}".format(province)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        department_facets = response.data["fields"]["department"]
        department_projects_after_filtering = 0
        for value in department_facets:
            if department == value["text"]:
                department_projects_after_filtering = value["count"]
        self.assertEqual(department_projects_after_filtering, 1)

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
        department_projects_before_filtering = 0
        for value in department_facets:
            if department == value["text"]:
                department_projects_before_filtering = value["count"]
        self.assertEqual(department_projects_before_filtering, 2)

        data = {"q": province}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        department_facets = response.data["fields"]["department"]
        department_projects_after_filtering = 0
        for value in department_facets:
            if department == value["text"]:
                department_projects_after_filtering = value["count"]
        self.assertEqual(department_projects_after_filtering, 1)


class InfraProjectAPIStatusTestCase(APITestCase):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file = open(EMPTY_FILE_PATH, "rb")
        self.url = reverse("infrastructure-project-api-list")
        self.facet_url = reverse("infrastructure-project-api-facets")
        fin_year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(self.file),
        )
        self.project_1 = InfraProject.objects.create(IRM_project_id=1)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            province="Eastern Cape",
            status="Construction",
            estimated_completion_date=self.date,
        )
        self.project_2 = InfraProject.objects.create(IRM_project_id=2)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            province="Free State",
            status="Construction",
            estimated_completion_date=self.date,
        )
        self.project_3 = InfraProject.objects.create(IRM_project_id=3)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_3,
            province="Eastern Cape",
            status="Completed",
            estimated_completion_date=self.date,
        )
        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file.close()

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
        province_projects_before_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                province_projects_before_filtering = value["count"]

        self.assertEqual(province_projects_before_filtering, 2)

        data = {"selected_facets": "status_exact:{0}".format(status_)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        province_facets = response.data["fields"]["province"]
        province_projects_after_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                province_projects_after_filtering = value["count"]

        self.assertEqual(province_projects_after_filtering, 1)


class InfraProjectAPIFundingSourceTestCase(APITestCase):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file = open(EMPTY_FILE_PATH, "rb")
        self.url = reverse("infrastructure-project-api-list")
        self.facet_url = reverse("infrastructure-project-api-facets")
        fin_year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(self.file),
        )
        self.project_1 = InfraProject.objects.create(IRM_project_id=1)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            province="Eastern Cape",
            primary_funding_source="Community Library Service Grant",
            estimated_completion_date=self.date,
        )
        self.project_2 = InfraProject.objects.create(IRM_project_id=2)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            province="Free State",
            primary_funding_source="Community Library Service Grant",
            estimated_completion_date=self.date,
        )
        self.project_3 = InfraProject.objects.create(IRM_project_id=3)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_3,
            province="Eastern Cape",
            primary_funding_source="Equitable Share",
            estimated_completion_date=self.date,
        )
        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file.close()

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
        province_projects_before_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                province_projects_before_filtering = value["count"]

        self.assertEqual(province_projects_before_filtering, 2)

        data = {"selected_facets": "primary_funding_source_exact:{0}".format(source)}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        province_facets = response.data["fields"]["province"]
        province_projects_after_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                province_projects_after_filtering = value["count"]

        self.assertEqual(province_projects_after_filtering, 1)


class InfraProjectAPIProjectNameTestCase(APITestCase):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file = open(EMPTY_FILE_PATH, "rb")
        self.url = reverse("infrastructure-project-api-list")
        self.facet_url = reverse("infrastructure-project-api-facets")
        fin_year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(self.file),
        )
        self.project_1 = InfraProject.objects.create(IRM_project_id=1)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            name="Project 1",
            province="Eastern Cape",
            estimated_completion_date=self.date,
        )
        self.project_2 = InfraProject.objects.create(IRM_project_id=2)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            name="Project 2",
            province="Eastern Cape",
            estimated_completion_date=self.date,
        )
        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file.close()

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
        province = "Eastern Cape"

        response = self.client.get(self.facet_url)
        province_facets = response.data["fields"]["province"]
        province_projects_before_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                province_projects_before_filtering = value["count"]

        self.assertEqual(province_projects_before_filtering, 2)

        data = {"q": name}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        province_facets = response.data["fields"]["province"]
        province_projects_after_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                province_projects_after_filtering = value["count"]

        self.assertEqual(province_projects_after_filtering, 1)


class InfraProjectAPIMunicipalityTestCase(APITestCase):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file = open(EMPTY_FILE_PATH, "rb")
        self.url = reverse("infrastructure-project-api-list")
        self.facet_url = reverse("infrastructure-project-api-facets")
        fin_year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(self.file),
        )
        self.project_1 = InfraProject.objects.create(IRM_project_id=1)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            name="Project 1",
            province="Eastern Cape",
            local_municipality="Local 1",
            estimated_completion_date=self.date,
        )
        self.project_2 = InfraProject.objects.create(IRM_project_id=2)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            name="Project 2",
            province="Eastern Cape",
            local_municipality="Local 2",
            estimated_completion_date=self.date,
        )
        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file.close()

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
        province = "Eastern Cape"
        municipality = "Local 1"

        response = self.client.get(self.facet_url)
        province_facets = response.data["fields"]["province"]
        province_projects_before_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                province_projects_before_filtering = value["count"]

        self.assertEqual(province_projects_before_filtering, 2)

        data = {"q": municipality}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        province_facets = response.data["fields"]["province"]
        province_projects_after_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                province_projects_after_filtering = value["count"]

        self.assertEqual(province_projects_after_filtering, 1)


class InfraProjectAPIContractorTestCase(APITestCase):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file = open(EMPTY_FILE_PATH, "rb")
        self.url = reverse("infrastructure-project-api-list")
        self.facet_url = reverse("infrastructure-project-api-facets")
        fin_year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(self.file),
        )
        self.project_1 = InfraProject.objects.create(IRM_project_id=1)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            name="Project 1",
            main_contractor="Contractor 1",
            province="Eastern Cape",
            estimated_completion_date=self.date,
        )
        self.project_2 = InfraProject.objects.create(IRM_project_id=2)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            name="Project 2",
            main_contractor="Contractor 2",
            province="Eastern Cape",
            estimated_completion_date=self.date,
        )
        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file.close()

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
        contractor = "Contractor 1"
        province = "Eastern Cape"

        response = self.client.get(self.facet_url)
        province_facets = response.data["fields"]["province"]
        province_projects_before_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                province_projects_before_filtering = value["count"]

        self.assertEqual(province_projects_before_filtering, 2)

        data = {"q": contractor}
        response = self.client.get(self.facet_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        province_facets = response.data["fields"]["province"]
        province_projects_after_filtering = 0
        for value in province_facets:
            if province == value["text"]:
                province_projects_after_filtering = value["count"]

        self.assertEqual(province_projects_after_filtering, 1)


class InfraProjectAPISearchMultipleFieldsTestCase(APITestCase):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file = open(EMPTY_FILE_PATH, "rb")
        self.url = reverse("infrastructure-project-api-list")
        self.facet_url = reverse("infrastructure-project-api-facets")
        fin_year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(self.file),
        )
        self.project_1 = InfraProject.objects.create(IRM_project_id=1)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            name="Something School",
            province="Eastern Cape",
            estimated_completion_date=date(year=2020, month=6, day=1),
        )
        self.project_2 = InfraProject.objects.create(IRM_project_id=2)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            name="Project 2",
            province="Eastern Cape",
            estimated_completion_date=date(year=2020, month=6, day=1),
        )
        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file.close()

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


class InfraProjectAPIURLPathTestCase(APITestCase):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file = open(EMPTY_FILE_PATH, "rb")
        fin_year = FinancialYear.objects.create(slug="2030-31", published=True)
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.irm_snapshot = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(self.file),
        )
        self.url = reverse("infrastructure-project-api-list")
        self.facet_url = reverse("infrastructure-project-api-facets")
        self.project = InfraProject.objects.create(IRM_project_id=1)
        InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project,
            name="Project 1",
            estimated_completion_date=date(year=2020, month=1, day=1),
            province="Fake prov",
            department="Fake dept",
        )

        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file.close()

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


class InfraProjectSnapshotTestCase(APITestCase):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file_1 = open(EMPTY_FILE_PATH, "rb")
        self.file_2 = open(EMPTY_FILE_PATH, "rb")
        self.project = InfraProject.objects.create(IRM_project_id=1)
        fin_year = FinancialYear.objects.create(slug="2030-31", published=True)
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        self.quarter_1 = Quarter.objects.create(number=1)
        self.quarter_2 = Quarter.objects.create(number=2)
        self.date_1 = date(year=2050, month=1, day=1)
        self.irm_snapshot_1 = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter_1,
            date_taken=self.date_1,
            file=File(self.file_1),
        )
        self.project_snapshot_1 = InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot_1,
            project=self.project,
            local_municipality="MUNI A",
            estimated_completion_date=date(year=2020, month=1, day=1),
            department="Fake Dept",
            province="Fake Prov",
        )

        self.irm_snapshot_2 = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter_2,
            date_taken=self.date_1,
            file=File(self.file_2),
        )
        self.project_snapshot_2 = InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot_2,
            project=self.project,
            local_municipality="MUNI B",
            estimated_completion_date=date(year=2020, month=1, day=1),
            department="Fake Dept",
            province="Fake Prov",
        )

    def tearDown(self):
        self.file_1.close()
        self.file_2.close()

    def test_latest_status_in_the_content(self):
        response = self.client.get(self.project.get_absolute_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "MUNI B")
        self.assertNotContains(response, "MUNI A")

    def test_latest_in_the_same_year(self):
        latest = self.project.project_snapshots.latest()

        self.assertEqual(self.project_snapshot_2, latest)


class InfraProjectSnapshotDifferentYearsTestCase(APITestCase):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file_1 = open(EMPTY_FILE_PATH, "rb")
        self.file_2 = open(EMPTY_FILE_PATH, "rb")
        self.project = InfraProject.objects.create(IRM_project_id=1)
        fin_year_1 = FinancialYear.objects.create(slug="2030-31")
        fin_year_2 = FinancialYear.objects.create(slug="2031-32")
        self.sphere_1 = Sphere.objects.create(
            financial_year=fin_year_1, name="Provincial"
        )
        self.sphere_2 = Sphere.objects.create(
            financial_year=fin_year_2, name="Provincial"
        )
        self.quarter_1 = Quarter.objects.create(number=1)
        self.date_1 = date(year=2050, month=1, day=1)
        self.date_2 = date(year=2070, month=1, day=1)
        self.irm_snapshot_1 = IRMSnapshot.objects.create(
            sphere=self.sphere_1,
            quarter=self.quarter_1,
            date_taken=self.date_1,
            file=File(self.file_1),
        )
        self.project_snapshot_1 = InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot_1,
            project=self.project,
            estimated_completion_date=date(year=2020, month=1, day=1),
        )

        self.irm_snapshot_2 = IRMSnapshot.objects.create(
            sphere=self.sphere_2,
            quarter=self.quarter_1,
            date_taken=self.date_2,
            file=File(self.file_2),
        )
        self.project_snapshot_2 = InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot_2,
            project=self.project,
            estimated_completion_date=date(year=2020, month=1, day=1),
        )

    def tearDown(self):
        self.file_1.close()
        self.file_2.close()

    def test_latest_in_different_years(self):
        latest = self.project.project_snapshots.latest()

        self.assertEqual(self.project_snapshot_2, latest)


class InfraProjectFullTextSearchTestCase(APITestCase):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file = open(EMPTY_FILE_PATH, "rb")
        self.url = reverse("infrastructure-project-api-list")
        fin_year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        self.quarter = Quarter.objects.create(number=1)
        self.date = date(year=2050, month=1, day=1)
        self.project_1 = InfraProject.objects.create(IRM_project_id=1)

        self.irm_snapshot = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=self.quarter,
            date_taken=self.date,
            file=File(self.file),
        )
        self.project_snapshot_1 = InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_1,
            name="Blue School",
            province="Eastern Cape",
            estimated_completion_date=date(year=2020, month=1, day=1),
        )

        self.project_2 = InfraProject.objects.create(IRM_project_id=2)
        self.project_snapshot_2 = InfraProjectSnapshot.objects.create(
            irm_snapshot=self.irm_snapshot,
            project=self.project_2,
            name="Red School",
            province="Limpopo",
            estimated_completion_date=date(year=2020, month=1, day=1),
        )
        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file.close()

    def test_correct_project_returned(self):
        search = "Eastern Cape School"
        data = {"q": search}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Blue School")
        self.assertNotContains(response, "Red School")
        self.assertEqual(
            response.data["csv_download_url"],
            "/infrastructure-projects/full/search/csv?q=Eastern+Cape+School",
        )


class InfraProjectSearchCSVTestCaseMixin:
    def _test_csv_content_correctness(self, csv_reader, items_to_compare):
        self.assertEqual(len(list(csv_reader)), len(items_to_compare))
        for index, row in enumerate(csv_reader):
            # Verify all the serializer fields are present in the CSV
            self.assertListEqual(
                list(row.keys()), InfraProjectCSVSerializer.Meta.fields
            )

            # Verify correctness of the name of project field between CSV and model
            self.assertEqual(items_to_compare[index].name, row["name"])

            # Verify correctness of the string representation of irm_snapshot between CSV and model
            self.assertEqual(
                str(items_to_compare[index].irm_snapshot), row["irm_snapshot"]
            )

            # Verify correctness of province field of project between CSV and model
            self.assertEqual(items_to_compare[index].province, row["province"])

            # Verify correctness of completion date field of project between CSV and model
            self.assertEqual(
                items_to_compare[index].estimated_completion_date.strftime("%Y-%m-%d"),
                row["estimated_completion_date"],
            )

            # Verify correctness of adjusted_appropriation_professional_fees field of project between CSV and model
            self.assertEqual(
                float(items_to_compare[index].adjusted_appropriation_professional_fees),
                float(row["adjusted_appropriation_professional_fees"]),
            )

    def _test_response_correctness(self, response, filename):
        self.assertEqual(response.status_code, 200)
        self.assertEquals(
            response.get("Content-Disposition"),
            'attachment; filename="{}"'.format(filename),
        )


class InfraProjectIRMSnapshotCSVDownloadTestCase(
    APITestCase, InfraProjectSearchCSVTestCaseMixin
):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file1 = open(EMPTY_FILE_PATH, "rb")
        self.file1_1_older = open(EMPTY_FILE_PATH, "rb")
        self.file1_2_older = open(EMPTY_FILE_PATH, "rb")
        self.file2 = open(EMPTY_FILE_PATH, "rb")
        self.url = reverse("infrastructure-project-api-list")
        fin_year_1 = FinancialYear.objects.create(slug="2030-31")
        sphere_1 = Sphere.objects.create(financial_year=fin_year_1, name="Provincial")
        fin_year_2 = FinancialYear.objects.create(slug="2031-32")
        sphere_2 = Sphere.objects.create(financial_year=fin_year_2, name="Provincial")

        irm_snapshot_1 = IRMSnapshot.objects.create(
            sphere=sphere_1,
            quarter=Quarter.objects.create(number=3),
            date_taken=datetime(year=2050, month=1, day=1),
            file=File(self.file1),
        )
        irm_snapshot_1_1_older = IRMSnapshot.objects.create(
            sphere=sphere_2,
            quarter=Quarter.objects.create(number=1),
            date_taken=datetime(year=2050, month=1, day=1),
            file=File(self.file1_1_older),
        )
        irm_snapshot_1_2_older = IRMSnapshot.objects.create(
            sphere=sphere_1,
            quarter=Quarter.objects.get(number=1),
            date_taken=datetime(year=2050, month=1, day=1),
            file=File(self.file1_2_older),
        )
        project_1 = InfraProject.objects.create(IRM_project_id=1)
        self.project_snapshot_1 = InfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1,
            project=project_1,
            name="Blue School",
            province="Eastern Cape",
            estimated_completion_date=date(year=2020, month=1, day=1),
            adjusted_appropriation_professional_fees=1.0,
        )
        self.project_snapshot_1_1_older = InfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1_1_older,
            project=project_1,
            name="Blue School",
            province="Eastern Cape",
            estimated_completion_date=date(year=2020, month=1, day=1),
            adjusted_appropriation_professional_fees=1.0,
        )

        self.project_snapshot_1_2_older = InfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1_2_older,
            project=project_1,
            name="Blue School",
            province="Eastern Cape",
            estimated_completion_date=date(year=2020, month=1, day=1),
            adjusted_appropriation_professional_fees=1.0,
        )

        irm_snapshot_2 = IRMSnapshot.objects.create(
            sphere=sphere_2,
            quarter=Quarter.objects.create(number=2),
            date_taken=datetime(year=2050, month=1, day=1),
            file=File(self.file2),
        )
        project_2 = InfraProject.objects.create(IRM_project_id=2)
        self.project_snapshot_2 = InfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2,
            project=project_2,
            name="Red School",
            province="Limpopo",
            estimated_completion_date=date(year=2020, month=1, day=1),
            adjusted_appropriation_professional_fees=2.0,
        )
        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file1.close()
        self.file2.close()
        self.file1_1_older.close()
        self.file1_2_older.close()

    def test_csv_download_empty_file(self):
        """
        Verifies 1) correct filename, 2) header but zero rows of data present
        """
        data = {"q": "data that won't be found"}
        response = self.client.get(self.url, data)
        self.assertEqual(len(response.data["results"]), 0)

        csv_download_url = response.data["csv_download_url"]
        response = self.client.get(csv_download_url)
        self._test_response_correctness(
            response, "infrastructure-projects-q-data-that-won-t-be-found.csv",
        )

        content = b"".join(response.streaming_content)
        csv_reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        self.assertListEqual(
            csv_reader.fieldnames, InfraProjectCSVSerializer.Meta.fields
        )
        self.assertEqual(len(list(csv_reader)), 0)

    def test_csv_download_with_all_projects(self):
        """
        Verifies that 1) correct filename, 2) correct header, number of rows for all projects
        """
        response = self.client.get(self.url)
        self.assertEqual(len(response.data["results"]), 2)

        csv_download_url = response.data["csv_download_url"]
        response = self.client.get(csv_download_url)
        self._test_response_correctness(response, "infrastructure-projects.csv")

        content = b"".join(response.streaming_content)
        csv_reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        items_to_compare = [self.project_snapshot_1, self.project_snapshot_2]
        self._test_csv_content_correctness(csv_reader, items_to_compare)

    def test_csv_download_with_found_project(self):
        search = "Eastern Cape School"
        data = {"q": search}
        response = self.client.get(self.url, data)
        self.assertEqual(len(response.data["results"]), 1)

        csv_download_url = response.data["csv_download_url"]
        response = self.client.get(csv_download_url)
        self._test_response_correctness(
            response, "infrastructure-projects-q-eastern-cape-school.csv"
        )

        content = b"".join(response.streaming_content)
        csv_reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        items_to_compare = [self.project_snapshot_1]
        self._test_csv_content_correctness(csv_reader, items_to_compare)


class InfraProjectIRMSnapshotCSVDownloadMoreThanPageSizeTestCase(
    APITestCase, InfraProjectSearchCSVTestCaseMixin
):
    def setUp(self):
        InfraProjectIndex().clear()
        self.page_size = settings.REST_FRAMEWORK.get("PAGE_SIZE", 20)
        self.number_of_projects = self.page_size * 2
        self.file = open(EMPTY_FILE_PATH, "rb")
        self.url = reverse("infrastructure-project-api-list")

        for index in range(self.number_of_projects):
            self.create_project(index)

        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()

    def create_project(self, index):
        file = open(EMPTY_FILE_PATH, "rb")
        financial_year = FinancialYear.objects.create(
            slug=FinancialYear.slug_from_year_start(str(2000 + index))
        )
        sphere = Sphere.objects.create(financial_year=financial_year, name="Provincial")
        irm_snapshot = IRMSnapshot.objects.create(
            sphere=sphere,
            quarter=Quarter.objects.get_or_create(number=1)[0],
            date_taken=date(year=2050, month=1, day=1),
            file=File(file),
        )
        InfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot,
            project=InfraProject.objects.create(IRM_project_id=index),
            name="Blue School",
            province="Eastern Cape",
            estimated_completion_date=date(year=2020, month=1, day=1),
            adjusted_appropriation_professional_fees=1.0,
        )
        file.close()

    def test_csv_download_with_more_existing_objects_than_page_size(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.data["results"]), self.page_size)

        csv_download_url = response.data["csv_download_url"]
        response = self.client.get(csv_download_url)
        self._test_response_correctness(response, "infrastructure-projects.csv")

        content = b"".join(response.streaming_content)
        csv_reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        self.assertEqual(len(list(csv_reader)), self.number_of_projects)


class InfraProjectIRMSnapshotDetailCSVDownloadTestCase(
    APITestCase, InfraProjectSearchCSVTestCaseMixin
):
    def setUp(self):
        InfraProjectIndex().clear()
        self.file1 = open(EMPTY_FILE_PATH, "rb")
        self.file2 = open(EMPTY_FILE_PATH, "rb")
        fin_year = FinancialYear.objects.create(slug="2030-31")
        self.sphere = Sphere.objects.create(financial_year=fin_year, name="Provincial")
        fin_year_2 = FinancialYear.objects.create(slug="2031-32")
        self.sphere_2 = Sphere.objects.create(
            financial_year=fin_year_2, name="Provincial"
        )

        irm_snapshot_1 = IRMSnapshot.objects.create(
            sphere=self.sphere,
            quarter=Quarter.objects.create(number=1),
            date_taken=datetime(year=2050, month=1, day=1),
            file=File(self.file1),
        )
        irm_snapshot_2 = IRMSnapshot.objects.create(
            sphere=self.sphere_2,
            quarter=Quarter.objects.create(number=2),
            date_taken=datetime(year=2050, month=1, day=1),
            file=File(self.file2),
        )
        self.project = InfraProject.objects.create(IRM_project_id=1)
        self.project_snapshot_1 = InfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_1,
            project=self.project,
            name="Blue School",
            province="Eastern Cape",
            estimated_completion_date=date(year=2020, month=1, day=1),
            adjusted_appropriation_professional_fees=1.0,
        )
        self.project_snapshot_2 = InfraProjectSnapshot.objects.create(
            irm_snapshot=irm_snapshot_2,
            project=self.project,
            name="Red School",
            province="Limpopo",
            estimated_completion_date=date(year=2020, month=1, day=1),
            adjusted_appropriation_professional_fees=2.0,
        )

        InfraProjectIndex().reindex()

    def tearDown(self):
        InfraProjectIndex().clear()
        self.file1.close()
        self.file2.close()

    def test_404_if_there_is_no_project(self):
        data = {"id": 9999999, "slug": "slug"}
        url = reverse("infra-project-detail-csv-download", kwargs=data)
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, 404)

    def test_csv_download(self):
        data = {"id": self.project.id, "slug": self.project.get_slug()}
        url = reverse("infra-project-detail-csv-download", kwargs=data)
        response = self.client.get(url, data)
        self._test_response_correctness(
            response, filename="{}.csv".format(self.project.get_slug())
        )

        content = b"".join(response.streaming_content)
        csv_reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        items_to_compare = [self.project_snapshot_1, self.project_snapshot_2]
        self._test_csv_content_correctness(csv_reader, items_to_compare)
