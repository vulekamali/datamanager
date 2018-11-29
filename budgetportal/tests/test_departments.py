from django.test import TestCase, Client
from budgetportal.models import (
    FinancialYear,
    Sphere,
    Government,
    Department,
)
import yaml


class BasicPagesTestCase(TestCase):
    def setUp(self):
        FinancialYear.objects.create(slug="2015-16")
        FinancialYear.objects.create(slug="2016-17")
        FinancialYear.objects.create(slug="2017-18")
        FinancialYear.objects.create(slug="2018-19")
        FinancialYear.objects.create(slug="2019-20")
        for year in FinancialYear.objects.all():
            # spheres
            national = Sphere.objects.create(financial_year=year, name='National')
            provincial = Sphere.objects.create(financial_year=year, name='Provincial')

            # governments
            south_africa = Government.objects.create(sphere=national, name='South Africa')
            fake_central = Government.objects.create(sphere=provincial, name='Fake Central')
            fake_south = Government.objects.create(sphere=provincial, name='Fake South')

            # departments
            Department.objects.create(
                government=south_africa,
                name='The Presidency',
                vote_number=1,
                intro=""
            )
            Department.objects.create(
                government=south_africa,
                name='Parliament',
                vote_number=2,
                intro=""
            )
            Department.objects.create(
                government=fake_central,
                name="Premier's Office",
                vote_number=1,
                intro=""
            )
            Department.objects.create(
                government=fake_central,
                name="Education",
                vote_number=2,
                intro=""
            )
            Department.objects.create(
                government=fake_south,
                name="Premier's Office",
                vote_number=1,
                intro=""
            )

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
