# !/usr/bin/python
# -*- coding: utf-8 -*

from django.test import override_settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from budgetportal.models import (
    InfrastructureProjectPart, FinancialYear)
from budgetportal.tests.helpers import BaseSeleniumTestCase


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class PPPProjectTestCase(BaseSeleniumTestCase):
    fixtures = ["test-infrastructure-pages-detail"]

    def setUp(self):
        super(PPPProjectTestCase, self).setUp()
        FinancialYear.objects.create(slug="2019-20", published=True)
        self.project = InfrastructureProjectPart.objects.filter(
            administration_type="PPP"
        ).first()

    def test_project_detail_page_fields(self):
        url = self.project.get_absolute_url()
        self.selenium.get("%s%s" % (self.live_server_url, url))
        selenium = self.selenium
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#partnership-type")))
        partnership_type = selenium.find_element_by_css_selector("#partnership-type").text
        project_title = selenium.find_element_by_css_selector("#project-title").text
        budget = selenium.find_element_by_css_selector("#total-budget").text
        line = selenium.find_element_by_css_selector(".recharts-line")
        self.assertEqual(partnership_type, u"Fake Partnership")
        self.assertEqual(project_title, u"School Infrastructure Backlogs Grant")
        self.assertEqual(budget, u"R4 billion")
        self.assertEqual(line.is_displayed(), True)
