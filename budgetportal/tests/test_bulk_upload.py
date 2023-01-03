import os

from allauth.account.models import EmailAddress
from budgetportal.models import Department, FinancialYear, Government, Sphere
from budgetportal.tests.helpers import BaseSeleniumTestCase
from ckanapi import NotFound
from django.contrib.auth.models import User
from mock import patch
from selenium.webdriver.support.ui import Select

USERNAME = "testuser"
EMAIL = "testuser@domain.com"
PASSWORD = "12345"


class BulkUploadTestCase(BaseSeleniumTestCase):
    def setUp(self):
        year = FinancialYear.objects.create(slug="2030-31")
        Sphere.objects.create(financial_year=year, name="Provincial")
        self.national = Sphere.objects.create(financial_year=year, name="National")
        south_africa = Government.objects.create(
            sphere=self.national, name="South Africa"
        )
        Department.objects.create(
            government=south_africa, name="The Presidency", vote_number=1, intro=""
        )

        user = User.objects.create_user(
            username=USERNAME,
            password=PASSWORD,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        EmailAddress.objects.create(user=user, email=EMAIL, verified=True)

        self.path = os.path.dirname(__file__)

        # Patch CKAN API
        self.ckan_patch = patch("budgetportal.datasets.ckan")
        self.CKANMockClass = self.ckan_patch.start()
        self.CKANMockClass.action.package_search.return_value = {"results": []}
        self.CKANMockClass.action.package_show.side_effect = NotFound()
        self.CKANMockClass.action.group_show.side_effect = NotFound()
        self.addCleanup(self.ckan_patch.stop)

        self.ckan_patch2 = patch("budgetportal.models.government.ckan")
        self.CKANMockClass2 = self.ckan_patch2.start()
        self.CKANMockClass2.action.package_search.return_value = {"results": []}
        self.CKANMockClass2.action.package_show.side_effect = NotFound()
        self.CKANMockClass2.action.group_show.side_effect = NotFound()
        self.addCleanup(self.ckan_patch2.stop)

        super(BulkUploadTestCase, self).setUp()

    def test_bulk_upload(self):
        selenium = self.selenium

        ## Login
        selenium.get("%s%s" % (self.live_server_url, "/admin/"))
        username = selenium.find_element_by_id("id_login")
        password = selenium.find_element_by_id("id_password")
        submit_button = selenium.find_element_by_css_selector('button[type="submit"]')
        username.send_keys(EMAIL)
        password.send_keys(PASSWORD)
        submit_button.click()

        ## Navigate to bulk upload
        selenium.find_element_by_link_text("Bulk Upload").click()

        # Ensure the sphere exists and can be selected
        sphere_select = Select(selenium.find_element_by_id("id_sphere"))
        sphere_select.select_by_visible_text(str(self.national))

        file_input = selenium.find_element_by_id("id_file")
        file_input.send_keys(self.path + "/test_data/test_bulk_upload_metadata.xlsx")

        submit_input = selenium.find_element_by_css_selector('input[type="submit"]')
        submit_input.click()

        preview_rows = selenium.find_elements_by_css_selector("#bulk-upload-preview tr")
        self.assertEqual(len(preview_rows), 5)
