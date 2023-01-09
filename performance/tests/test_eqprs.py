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
        self.correct_csv = """ReportTitle,Textbox95,Textbox80,Textbox81,Textbox82,Textbox83
QPR for FY 2021-22 Provincial Institutions Oversight Performance  Report as of ( FY 2021-22),"Location/s: Eastern Cape, Free State",InstitutionType:   Provincial,Institution:   Health,FinancialYear:   FY 2021-22,"Report Printed On:   Wednesday, September 28, 2022 11:11:10 AM"

Sector,Institution,Programme,SubProgramme,Location,Frequency,Indicator,Type,SubType,Outcome,Cluster,Target_Q1,ActualOutput_Q1,ReasonforDeviation_Q1,CorrectiveAction_Q1,OTP_Q1,National_Q1,Target_Q2,ActualOutput_Q2,ReasonforDeviation_Q2,CorrectiveAction_Q2,OTP_Q2,National_Q2,Target_Q3,ActualOutput_Q3,ReasonforDeviation_Q3,CorrectiveAction_Q3,OTP_Q3,National_Q3,Target_Q4,ActualOutput_Q4,ReasonforDeviation_Q4,CorrectiveAction_Q4,OTP_Q4,National_Q4,AnnualTarget_Summary2,Preliminary_Summary2,PrelimaryAudited_Summary2,ReasonforDeviation_Summary,CorrectiveAction_Summary,OTP_Summary,National_Summary,ValidatedAudited_Summary2,UID
Health,Health,Eastern Cape,Programme 1: Administration,Sub-Programme 1.1: Office of the MEC,Quarterly,9.1.2 Number of statutory documents tabled at Legislature,Non-Standardized,Max,"Priority 3: Education, Skills And Health","The Social Protection, Community and Human Development cluster",0,0,There is no target for quarter one,,,,1,2,Target achieved,,,,2,2,Target achieved,,,,5,8,All statutory documents submitted.,,,,8,8,8,Target achieved ,,,,,291
Health,Health,Eastern Cape,Programme 1: Administration,Sub-Programme 1.2: Management,Annually,6.4.1 Holistic Human  Resources for Health (HRH) strategy  approved ,Non-Standardized,Not  Applicable,"Priority 3: Education, Skills And Health","The Social Protection, Community and Human Development cluster",,,,,,,,,,,,,,,,,,,,,,,,,Approved HRH Strategy,A draft plan for Human Resources for Health (HRH has been produced,Draft HRH Strategy,"The HRH 2030 Strategy Plan is in progress.
The Task Team has produced a draft HRH 2030 Plan by the end of the 4th quarter.
 The Task Team requires the additional capacity of a qualified Technical Advisor to conclude this plan.  
",,,,,291"""
        self.mocked_request = get_mocked_request(self.superuser)

    def test_report_name_validation(self):
        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser,
        )
        performance.admin.parse_and_process_csv('', test_element.id)
        test_element.refresh_from_db()
        assert test_element.import_report == """Report preamble must be for one of 
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
        sphere = Sphere.objects.create(name="Test Sphere", financial_year=fy)
        government = Government.objects.create(name="Test Government", sphere=sphere)
        department = Department.objects.create(name="Health", government=government, vote_number=1)

        test_element = EQPRSFileUpload.objects.create(
            user=self.superuser,
        )
        performance.admin.parse_and_process_csv(self.correct_csv, test_element.id)
        assert Indicator.objects.all().count() == 2

        indicator = models.Indicator.objects.filter(id=1).first()
        assert indicator.indicator_name == "9.1.2 Number of statutory documents tabled at Legislature"
