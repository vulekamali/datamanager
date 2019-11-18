import os
from django.db.models import Count
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



@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class ProvInfraProjectAPITestCase(APITestCase):
    def setUp(self):
        """Create 30 Provincial Infrastructure Snapshots"""
        self.project = mommy.make(ProvInfraProject)
        self.url = reverse("provincial-infrastructure-project-api-list")

        self.provinces = ["Eastern Cape", "Free State"]
        self.statuses = ["Design", "Construction"]
        self.sources = [
            "Education Infrastructure Grant",
            "Community Library Service Grant",
        ]

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
                project=self.project,
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
        self.project_snapshot = self.project.project_snapshots.latest()

    def tearDown(self):
        connections['default']._index = self.old_unified_index
        super(ProvInfraProjectAPITestCase, self).tearDown()

    def test_filter_by_department(self):
        data = {"department": self.project_snapshot.department}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertEqual(result['name'], self.project_snapshot.name)
        self.assertEqual(result['department'], data['department'])

    def test_filter_by_province(self):
        province = "Eastern Cape"
        data = {"province": province}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertEqual(result['name'], self.project_snapshot.name)
        self.assertEqual(result['province'], data['province'])

    def test_filter_by_status(self):
        data = {"status": self.project_snapshot.status}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertEqual(result['name'], self.project_snapshot.name)
        self.assertEqual(result['status'], data['status'])

    def test_filter_by_funding_source(self):
        data = {"primary_funding_source":
                self.project_snapshot.primary_funding_source}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertEqual(result['name'], self.project_snapshot.name)
        self.assertEqual(result['primary_funding_source'],
                         data['primary_funding_source'])

    def test_search_by_project_name(self):
        data = {"search": self.project_snapshot.name}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertEqual(result['name'], self.project_snapshot.name)

    def test_search_by_province(self):
        data = {"search": self.project_snapshot.province}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertEqual(result['province'], self.project_snapshot.province)

    def test_search_multiple_fields(self):

        data = {"search": "Eastern Cape School"}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(results[0]["province"],
                         self.project_snapshot.province)
        self.assertEqual(results[0]["name"], self.project_snapshot.name)

    def test_url_path(self):
        data = {"search": self.project_snapshot.name}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["results"][0]
        url_path = result["url_path"]

        response = self.client.get(url_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, data['search'])


