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
import os
import sys

USERNAME = 'testuser'
EMAIL = 'testuser@domain.com'
PASSWORD = '12345'

# Hacky make sure we don't call out to openspending.
import requests
requests.get = Mock
requests.Session = Mock


class BulkUploadTestCase(StaticLiveServerTestCase):
    def setUp(self):
        year = FinancialYear.objects.create(slug="2030-31")
        Sphere.objects.create(financial_year=year, name='Provincial')
        self.national = Sphere.objects.create(financial_year=year, name='National')
        south_africa = Government.objects.create(sphere=self.national, name='South Africa')
        Department.objects.create(
            government=south_africa,
            name='The Presidency',
            vote_number=1,
            intro=""
        )

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

        # Mock CKAN API
        settings.CKAN.action = Mock()
        settings.CKAN.action.package_search.return_value = {'results': []}
        settings.CKAN.action.package_show.side_effect = NotFound()
        settings.CKAN.action.group_show.side_effect = NotFound()

        super(BulkUploadTestCase, self).setUp()


    def tearDown(self):
        self.selenium.quit()

        # https://stackoverflow.com/questions/14991244/how-do-i-capture-a-screenshot-if-my-nosetests-fail
        if sys.exc_info()[0]:  # Returns the info of exception being handled
            now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
            self.selenium.get_screenshot_as_file('%s.png' % now)
            super(BulkUploadTestCase, self).tearDown()

    def test_bulk_upload(self):
        selenium = self.selenium

        ## Login
        selenium.get('%s%s' % (self.live_server_url, '/admin/'))
        username = selenium.find_element_by_id('id_login')
        password = selenium.find_element_by_id('id_password')
        submit_button = selenium.find_element_by_css_selector('button[type="submit"]')
        username.send_keys(EMAIL)
        password.send_keys(PASSWORD)
        submit_button.click()

        ## Navigate to bulk upload
        selenium.find_element_by_link_text('Bulk Upload').click()

        # Ensure the sphere exists and can be selected
        sphere_select = Select(selenium.find_element_by_id("id_sphere"))
        sphere_select.select_by_visible_text(str(self.national))

        file_input = selenium.find_element_by_id('id_file')
        file_input.send_keys(self.path + "/test_data/test_bulk_upload_metadata.xlsx")

        submit_input = selenium.find_element_by_css_selector('input[type="submit"]')
        submit_input.click()

        preview_rows = selenium.find_elements_by_css_selector('#bulk-upload-preview tr')
        self.assertEqual(len(preview_rows), 5)
