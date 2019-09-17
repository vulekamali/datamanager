from budgetportal.models import (
    FinancialYear,
    Sphere,
    Government,
    Department,
)
from django.conf import settings
from django.test import TestCase, Client
from mock import patch, Mock
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

        ckan_patch = patch('budgetportal.datasets.ckan')
        CKANMockClass = ckan_patch.start()
        CKANMockClass.action.package_search.return_value = {'results': []}
        self.addCleanup(ckan_patch.stop)

        dataset_patch = patch('budgetportal.datasets.Dataset.get_latest_cpi_resource', return_value=('2018-19', '5b315ff0-55e9-4ba8-b88c-2d70093bfe9d'))
        dataset_patch.start()
        self.addCleanup(dataset_patch.stop)

    def test_overview_page(self):
        """Test that it exists and that the correct years are linked"""
        c = Client()
        response = c.get('/2019-20.yaml')
        content = yaml.load(response.content)
        self.assertEqual(content['selected_tab'], 'homepage')

    def test_department_detail_page_yaml(self):
        """Test that it exists and that the correct years are linked"""
        c = Client()
        response = c.get('/2019-20/national/departments/the-presidency.yaml')
        content = yaml.load(response.content)
        self.assertEqual(content['financial_years'][-1]['id'], '2019-20')
        self.assertEqual(content['financial_years'][0]['id'], '2016-17')

    def test_department_detail_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get('/2019-20/national/departments/the-presidency')
        content = response.content
        self.assertTrue(content.find('The Presidency budget data for the 2019-20 financial year'))

    def test_about_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get('/about')
        content = response.content
        self.assertTrue(content.find('Learn more about the new Online Budget Data Portal'))

    def test_events_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get('/events')
        content = response.content
        self.assertTrue(content.find('Join us at a Vulekamali event in your area'))

    def test_videos_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get('/videos')
        content = response.content
        self.assertTrue(content.find('Learn more about the new Online Budget Data Portal'))

    def test_terms_and_conditions_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get('/terms-and-conditions')
        content = response.content
        self.assertTrue(content.find('Users are encouraged to utilise this data'))

    def test_resources_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get('/resources')
        content = response.content
        self.assertTrue(content.find('The Budget Process and Public Participation'))

    def test_glossary_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get('/glossary')
        content = response.content
        self.assertTrue(content.find('Accounting officer'))

    def test_faq_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get('/faq')
        content = response.content
        self.assertTrue(content.find('When is the budget data updated?'))

    def test_guides_list_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get('/guides')
        content = response.content
        self.assertTrue(content.find("South Africa's National and Provincial budget data from National Treasury in partnership with IMALI YETHU."))

    def test_guide_page(self):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get('/guides/estimates-of-national-expenditure')
        content = response.content
        self.assertTrue(content.find("The Estimates of National Expenditure (ENE) publications describe in detail"))

    # def test_datasets_list_page(self):
    #     """Test that it loads and that some text is present"""
    #     c = Client()
    #     response = c.get('/datasets')
    #     content = response.content
    #     self.assertTrue(content.find("Data and Analysis"))
    #
    # def test_dataset_category_page(self):
    #     """Test that it loads and that some text is present"""
    #     c = Client()
    #     response = c.get('/datasets/adjusted-estimates-of-national-expenditure')
    #     content = response.content
    #     self.assertTrue(content.find("Adjustments to the expenditure plans."))
    #
    # def test_contributed_dataset_list_page(self):
    #     """Test that it loads and that some text is present"""
    #     c = Client()
    #     response = c.get('/datasets/contributed')
    #     content = response.content
    #     self.assertTrue(content.find("Contibuted data and documentation for South African government budgets"))

    # def test_contributed_dataset_page(self):
    #     """Test that it loads and that some text is present"""
    #     c = Client()
    #     response = c.get('/datasets/contributed/a-guide-to-conducting-social-audits-in-south-africa')
    #     content = response.content
    #     self.assertTrue(content.find("A Guide to Conducting Social Audits in South Africa"))
    #
    # def test_dataset_page(self):
    #     """Test that it loads and that some text is present"""
    #     c = Client()
    #     response = c.get('/datasets/annual-reports/annual-report-expenditure-2016-17')
    #     content = response.content
    #     self.assertTrue(content.find("Annual Report Expenditure 2016-17"))

    # def test_department_page(self):
    #     """Test that it loads and that some text is present"""
    #     c = Client()
    #     response = c.get('/2019-20/national/departments/agriculture-forestry-and-fisheries')
    #     content = response.content
    #     self.assertTrue(content.find("Agriculture, Forestry and Fisheries"))

    def test_search_page(self):
        """Test that it exists and that the correct years are linked"""
        c = Client()
        response = c.get('/2019-20/search-result.yaml')
        content = yaml.load(response.content)
        self.assertEqual(content['financial_years'][-1]['id'], '2019-20')
        self.assertEqual(content['financial_years'][0]['id'], '2016-17')
