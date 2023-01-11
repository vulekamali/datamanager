from django.test import TestCase, TransactionTestCase
from performance.admin import EQPRSFileUploadAdmin
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.contrib import admin
from performance.models import EQPRSFileUpload, Indicator
from budgetportal.models.government import Department, Government, Sphere, FinancialYear
from django.test import RequestFactory
from django.urls import reverse
from performance import models

import performance.admin
import os
import time

USERNAME = "testuser"
EMAIL = "testuser@domain.com"
PASSWORD = "12345"


def get_mocked_request(superuser):
    request = RequestFactory().get('/get/request')
    request.method = 'GET'
    request.user = superuser
    return request


class EQPRSFileUploadTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(
            username=USERNAME,
            password=PASSWORD,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname('performance'))
        )
        full_path = os.path.join(location, 'static', 'correct_data.csv')
        print('========= aaa =========')
        print(full_path)
        self.csv_file = open('../static/correct_data.csv', 'rb')
        print('========= bbb =========')
        self.correct_csv = """"""
        self.mocked_request = get_mocked_request(self.superuser)

    def test_report_name_validation(self):
        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser,
        )
        performance.admin.parse_and_process_csv('', test_element.id)
        test_element.refresh_from_db()
        assert test_element.import_report == """Report type must be for one of 
* Provincial Institutions Oversight Performance  Report 
* National Institutions Oversight Performance  Report 
"""

    def test_with_missing_department(self):
        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser,
        )
        performance.admin.parse_and_process_csv(self.correct_csv, test_element.id)
        test_element.refresh_from_db()
        assert test_element.import_report == """Department names that could not be matched on import : 
* Health 
"""

    def test_with_correct_csv(self):
        fy = FinancialYear.objects.create(slug="2021-22")
        sphere = Sphere.objects.create(name="Provincial", financial_year=fy)
        government = Government.objects.create(name="Eastern Cape", sphere=sphere)
        department = Department.objects.create(name="Health", government=government, vote_number=1)

        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser,
        )
        performance.admin.parse_and_process_csv(self.correct_csv, test_element.id)
        assert Indicator.objects.all().count() == 2

        indicator = models.Indicator.objects.filter(id=1).first()
        assert indicator.indicator_name == "9.1.2 Number of statutory documents tabled at Legislature"
