from budgetportal.models import (
    FinancialYear,
    Sphere,
    Government,
    Department,
)
from django.conf import settings
from django.test import TestCase, Client
from mock import patch
import yaml

# Hacky make sure we don't call out to openspending.
import requests
requests.get = Mock
requests.Session = Mock


class BasicPagesTestCase(TestCase):
    def setUp(self):
        FinancialYear.objects.create(slug="2015-16", published=True)
        FinancialYear.objects.create(slug="2016-17", published=True)
        FinancialYear.objects.create(slug="2017-18", published=True)
        FinancialYear.objects.create(slug="2018-19", published=True)
        FinancialYear.objects.create(slug="2019-20", published=True)
        for year in FinancialYear.objects.all():
            # spheres
            national = Sphere.objects.create(financial_year=year, name='National')
            Sphere.objects.create(financial_year=year, name='Provincial')

            # governments
            south_africa = Government.objects.create(sphere=national, name='South Africa')

            # departments
            Department.objects.create(
                government=south_africa,
                name='The Presidency',
                vote_number=1,
                intro=""
            )
        ckan_patch = patch('budgetportal.models.ckan')
        CKANMockClass = ckan_patch.start()
        CKANMockClass.action.package_search.return_value = {'results': []}
        self.addCleanup(ckan_patch.stop)

        dataset_patch = patch('budgetportal.models.Dataset.get_latest_cpi_resource', return_value=('2018-19', '5b315ff0-55e9-4ba8-b88c-2d70093bfe9d'))
        dataset_patch.start()
        self.addCleanup(dataset_patch.stop)

    def test_overview_page(self):
        """Test that it exists and that the correct years are linked"""
        c = Client()
        response = c.get('/2019-20.yaml')
        content = yaml.load(response.content)
        self.assertEqual(content['financial_years'][-1]['id'], '2019-20')
        self.assertEqual(content['financial_years'][0]['id'], '2016-17')


    def test_department_list_page(self):
        """Test that it exists and that the correct years are linked"""
        c = Client()
        response = c.get('/2019-20/departments.yaml')
        content = yaml.load(response.content)
        self.assertEqual(content['financial_years'][-1]['id'], '2019-20')
        self.assertEqual(content['financial_years'][0]['id'], '2016-17')

    def test_department_list_page_not_latest(self):
        """Test that it exists and that the correct years are linked"""
        c = Client()
        response = c.get('/2015-16/departments.yaml')
        content = yaml.load(response.content)
        self.assertEqual(content['financial_years'][-1]['id'], '2019-20')
        self.assertEqual(content['financial_years'][0]['id'], '2016-17')

    def test_department_detail_page(self):
        """Test that it exists and that the correct years are linked"""
        c = Client()
        response = c.get('/2019-20/national/departments/the-presidency.yaml')
        content = yaml.load(response.content)
        self.assertEqual(content['financial_years'][-1]['id'], '2019-20')
        self.assertEqual(content['financial_years'][0]['id'], '2016-17')

    def test_search_page(self):
        """Test that it exists and that the correct years are linked"""
        c = Client()
        response = c.get('/2019-20/search-result.yaml')
        content = yaml.load(response.content)
        self.assertEqual(content['financial_years'][-1]['id'], '2019-20')
        self.assertEqual(content['financial_years'][0]['id'], '2016-17')
