import os

from django.test import TestCase
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from budgetportal.models import FinancialYear, ProvInfraProject
from budgetportal.tests.helpers import BaseSeleniumTestCase

USERNAME = 'testuser'
EMAIL = 'testuser@domain.com'
PASSWORD = '12345'


class ProvInfraProjectsTestCase(BaseSeleniumTestCase):
    def setUp(self):
        user = User.objects.create_user(
            username=USERNAME,
            password=PASSWORD,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        EmailAddress.objects.create(
            user=user,
            email=EMAIL,
            verified=True,
        )
        self.path = os.path.dirname(__file__)
        self.financial_year = FinancialYear.objects.create(slug="2019-20")

        super(ProvInfraProjectsTestCase, self).setUp()

    def test_upload_xlsx_for_prov_infra_projects(self):
        filename = 'budgetportal/tests/test_data/test_import_prov_infra_projects.xlsx'

        selenium = self.selenium

        # Login
        selenium.get('%s%s' % (self.live_server_url, '/admin/'))
        username = selenium.find_element_by_id('id_login')
        password = selenium.find_element_by_id('id_password')
        submit_button = selenium.find_element_by_css_selector(
            'button[type="submit"]')
        username.send_keys(EMAIL)
        password.send_keys(PASSWORD)
        submit_button.click()

        selenium.find_element_by_link_text('Prov infra projects').click()
        selenium.find_element_by_link_text('IMPORT').click()

        file_import = selenium.find_element_by_id('id_import_file')
        financial_year_select = Select(selenium.find_element_by_id('id_financial_year'))
        file_import.send_keys(os.path.abspath(filename))
        financial_year_select.select_by_value(str(self.financial_year.id))
        selenium.find_element_by_css_selector(
            'input[type="submit"]').click()

        timeout = 2
        WebDriverWait(selenium, timeout).until(
            lambda driver: selenium.find_element_by_name('confirm'))

        selenium.find_element_by_name('confirm').click()

        timeout = 2
        WebDriverWait(selenium, timeout).until(
            lambda driver: selenium.find_element_by_class_name('success'))

        # check values of the first project
        first_project = ProvInfraProject.objects.get(IRM_project_id=30682)
        self.assertEqual(first_project.financial_year.slug, "2019-20")
        self.assertEqual(first_project.project_number, "W/50042423/WS")
        self.assertEqual(first_project.name, "BLUE JUNIOR SECONDARY SCHOOL")
        self.assertEqual(first_project.project_expenditure_total, 1315479)

        # check whether null values are imported as null, and 0 imported as 0
        self.assertEqual(first_project.contracted_construction_end_date, None)
        self.assertEqual(first_project.variation_orders, 0)

        # check whether parties/contractor mapping worked correctly
        self.assertEqual(first_project.program_implementing_agent, "DOPW")
        self.assertEqual(first_project.other_parties, None)

        # check whether all rows imported (There are 11 rows)
        count = ProvInfraProject.objects.count()
        self.assertEqual(count, 11)


