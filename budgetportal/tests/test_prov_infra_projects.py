import os
from datetime import timedelta, date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase
from model_mommy import mommy
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from selenium.webdriver.support.select import Select
from tablib import Dataset
import unittest
from django.test.utils import override_settings

from haystack import connections
from haystack.utils.loading import ConnectionHandler, UnifiedIndex

from budgetportal.models import FinancialYear, ProvInfraProject, \
    ProvInfraProjectSnapshot, IRMSnapshot, Quarter
from budgetportal import irm_preprocessor
from budgetportal.tests.helpers import BaseSeleniumTestCase

USERNAME = "testuser"
EMAIL = "testuser@domain.com"
PASSWORD = "12345"


from ..search_indexes import ProvInfraProjectIndex


TEST_INDEX = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': os.environ["SOLR_URL"],
        'INDEX_NAME': 'test_index',
    },
}


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

        # check whether parties/implementor mapping worked correctly
        self.assertEqual(first_project.program_implementing_agent, "DOPW")
        self.assertEqual(first_project.other_parties, None)

        # check whether all rows imported (There are 11 rows)
        count = ProvInfraProject.objects.count()
        self.assertEqual(count, 11)


@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class ProvInfraProjectAPITestCase(APITestCase):
    def setUp(self):
        """Create 30 Provincial Infrastructure Projects"""

        self.fin_year = FinancialYear.objects.create(slug="2030-31")
        self.url = reverse("provincial-infrastructure-project-api-list")
        self.provinces = ["Eastern Cape", "Free State"]
        self.statuses = ["Design", "Construction"]
        self.sources = [
            "Education Infrastructure Grant",
            "Community Library Service Grant",
        ]

        project = mommy.make(ProvInfraProject)
        for i in range(30):
            if i < 15:
                status = self.statuses[0]
                province = self.provinces[0]
                source = self.sources[0]
            else:
                status = self.statuses[1]
                province = self.provinces[1]
                source = self.sources[1]
            random_date = date.today() + timedelta(days=i)
            quarter = mommy.make(Quarter, number=i)
            financial_year = mommy.make(FinancialYear,
                                        slug='2030-{}'.format(i))
            irm_snapshot = mommy.make(IRMSnapshot, date_taken=random_date,
                                      quarter=quarter,
                                      financial_year=financial_year)
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
                estimated_completion_date=random_date
            )

        connections = ConnectionHandler(TEST_INDEX)
        super(ProvInfraProjectAPITestCase, self).setUp()

        self.old_unified_index = connections['default']._index
        self.ui = UnifiedIndex()
        self.mmi = ProvInfraProjectIndex()
        self.ui.build(indexes=[self.mmi])
        connections['default']._index = self.ui

        # Update the 'index'.
        backend = connections['default'].get_backend()
        backend.clear()
        backend.update(self.mmi, ProvInfraProject.objects.all())

    def tearDown(self):
        connections['default']._index = self.old_unified_index
        super(ProvInfraProjectAPITestCase, self).tearDown()

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
