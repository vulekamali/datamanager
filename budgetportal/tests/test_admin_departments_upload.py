from budgetportal.models import (
    FinancialYear,
    Sphere,
    Government,
    Department,
)
from allauth.account.models import EmailAddress
from ckanapi import NotFound
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from mock import Mock
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
import os
import sys

USERNAME = 'testuser'
EMAIL = 'testuser@domain.com'
PASSWORD = '12345'


class AdminDepartmentUploadTest(StaticLiveServerTestCase):
    def setUp(self):
        year = FinancialYear.objects.create(slug="2030-31")
        # spheres
        national = Sphere.objects.create(financial_year=year, name='National')
        provincial = Sphere.objects.create(
            financial_year=year, name='Provincial')
        # governments
        self.fake_national_government = Government.objects.create(
            sphere=national, name='South Africa')
        self.fake_provincial_government = Government.objects.create(
            sphere=provincial,
            name='Free State'
        )
        # Department.objects.create(
        #     government=south_africa,
        #     name='The Presidency',
        #     vote_number=1,
        #     intro=""
        # )

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

        self.selenium = webdriver.PhantomJS()

        self.path = os.path.dirname(__file__)

        super(AdminDepartmentUploadTest, self).setUp()

    def tearDown(self):
        self.selenium.quit()

        # https://stackoverflow.com/questions/14991244/how-do-i-capture-a-screenshot-if-my-nosetests-fail
        if sys.exc_info()[0]:  # Returns the info of exception being handled
            now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
            self.selenium.get_screenshot_as_file('%s.png' % now)
            super(AdminDepartmentUploadTest, self).tearDown()

    def test_upload_csv(self):
        filename = 'budgetportal/tests/test_data/test_management_commands_national_departments.csv'

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

        # Navigate to departments
        selenium.find_element_by_link_text('Departments').click()

        # Navigate to departments import page
        selenium.find_element_by_link_text('IMPORT').click()

        # Fill the form values
        file_import = selenium.find_element_by_id('id_import_file')
        sphere_select = Select(selenium.find_element_by_id('id_sphere'))

        file_import.send_keys(filename)
        sphere_select.select_by_index(1)

        selenium.find_element_by_css_selector(
            'input[type="submit"]').click()

        timeout = 2
        WebDriverWait(selenium, timeout).until(
            lambda driver: selenium.find_element_by_name('confirm'))

        selenium.find_element_by_name('confirm').click()

        timeout = 2
        WebDriverWait(selenium, timeout).until(
            lambda driver: selenium.find_element_by_class_name('success'))

        # Check that the departments were created

        presidency = Department.objects.get(
            government=self.fake_national_government, name='The Presidency')
        self.assertEqual(presidency.vote_number, 1)
        self.assertTrue(presidency.is_vote_primary)
        self.assertIn("To serve the president", presidency.intro)
        self.assertIn("Facilitate a common", presidency.intro)
        self.assertTrue(presidency.website_url, 'www.thepresidency.gov.za')

        parliament = Department.objects.get(
            government=self.fake_national_government, vote_number=2)
        self.assertEqual(parliament.name, 'Parliament')
        self.assertTrue(parliament.is_vote_primary)
        self.assertIn("Provide the support services", parliament.intro)
        self.assertIn("These are aligned", parliament.intro)
        self.assertTrue(parliament.website_url, 'www.parliament.gov.za')
