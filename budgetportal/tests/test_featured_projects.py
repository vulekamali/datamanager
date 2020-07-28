# !/usr/bin/python
# -*- coding: utf-8 -*
import time

from budgetportal.models import FinancialYear, InfrastructureProjectPart
from budgetportal.tests.helpers import BaseSeleniumTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class FeaturedProjectTestCase(BaseSeleniumTestCase):
    fixtures = ["test-infrastructure-pages-detail"]

    def setUp(self):
        super(FeaturedProjectTestCase, self).setUp()
        FinancialYear.objects.create(slug="2019-20", published=True)
        self.project_ppp = InfrastructureProjectPart.objects.filter(
            administration_type="PPP"
        ).first()
        self.project_national = InfrastructureProjectPart.objects.filter(pk=176).first()

    def test_national_project_detail_page_fields(self):
        url = self.project_national.get_absolute_url()
        self.selenium.get("%s%s" % (self.live_server_url, url))
        selenium = self.selenium
        self.wait.until(EC.presence_of_element_located((By.ID, "project-title")))
        info = (
            selenium.find_element_by_id("project-title")
            .find_element_by_xpath("..")
            .text.split("\n")
        )
        self.assertEqual(info[1], "School Infrastructure Backlogs Grant")
        self.assertEqual(info[2], "PROJECT STAGE: VARIOUS")
        self.assertEqual(info[4], "R9 billion")
        line = selenium.find_element_by_css_selector(".recharts-line")
        self.assertEqual(line.is_displayed(), True)

    def test_ppp_project_detail_page_fields(self):
        url = self.project_ppp.get_absolute_url()
        self.selenium.get("%s%s" % (self.live_server_url, url))
        selenium = self.selenium
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#project-title"))
        )
        partnership_type = selenium.find_element_by_css_selector(
            "#partnership-type"
        ).text
        project_title = selenium.find_element_by_css_selector("#project-title").text
        budget = selenium.find_element_by_css_selector("#total-budget").text
        line = selenium.find_element_by_css_selector(".recharts-line")
        self.assertEqual(partnership_type, u"Fake Partnership")
        self.assertEqual(project_title, u"School Infrastructure Backlogs Grant")
        self.assertEqual(budget, u"R4 billion")
        self.assertEqual(line.is_displayed(), True)
