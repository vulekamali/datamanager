import mock
from django.test import TestCase, LiveServerTestCase, Client

from budgetportal.models import InfrastructureProjectPart, MAPIT_POINT_API_URL, CKAN_DATASTORE_URL
import json
from mock import Mock

# Hacky make sure we don't call out to openspending.
import requests

requests.get = Mock
requests.Session = Mock


class ProjectedExpenditureTestCase(TestCase):
    """ Unit tests for get_projected_expenditure function """

    fixtures = [
        "test-infrastructure-pages-detail",
    ]

    def setUp(self):
        self.project = InfrastructureProjectPart.objects.all().first()

    def test_success(self):
        projected_expenditure = self.project.calculate_projected_expenditure()
        self.assertEqual(projected_expenditure, 5688808000.0)


class CoordinatesTestCase(TestCase):
    """ Unit tests for parsing coordinates """

    def test_success_simple_format(self):
        raw_coord_string = '-26.378582,27.654933'
        cleaned_coord_object = InfrastructureProjectPart._parse_coordinate(
            raw_coord_string
        )
        self.assertEqual(
            cleaned_coord_object,
            {
                'latitude': -26.378582,
                'longitude': 27.654933
            }
        )

    def test_failure_int_raises_type_error(self):
        invalid_coordinate = 25
        self.assertRaises(
            TypeError,
            InfrastructureProjectPart._parse_coordinate,
            invalid_coordinate
        )

    def test_failure_list_raises_type_error(self):
        invalid_coordinate = [25, 23]
        self.assertRaises(
            TypeError,
            InfrastructureProjectPart._parse_coordinate,
            invalid_coordinate
        )

    def test_success_multiple_coordinates(self):
        raw_coordinate_string = '-26.378582,27.654933 and -22.111222,23.333444'
        coords = InfrastructureProjectPart.clean_coordinates(raw_coordinate_string)
        self.assertIn(
            {
                'latitude': -26.378582,
                'longitude': 27.654933
            },
            coords
        )
        self.assertIn(
            {
                'latitude': -22.111222,
                'longitude': 23.333444
            },
            coords
        )

    def test_empty_response_for_invalid_value(self):
        raw_coordinate_string = 'test string with, no coords and'
        coords = InfrastructureProjectPart.clean_coordinates(raw_coordinate_string)
        self.assertEqual(coords, [])


class ExpenditureTestCase(TestCase):
    """ Unit tests for expenditure functions """

    fixtures = [
        "test-infrastructure-pages-detail",
    ]

    def setUp(self):
        self.project = InfrastructureProjectPart.objects.all().first()

    def test_success_build_expenditure_item(self):
        expenditure_item = InfrastructureProjectPart._build_expenditure_item(self.project)
        self.assertEqual(
            expenditure_item,
            {
                'year': self.project.financial_year,
                'amount': self.project.amount,
                'budget_phase': self.project.budget_phase
            }
        )

    def test_success_build_complete_expenditure(self):
        complete_expenditure = self.project.build_complete_expenditure()
        self.assertIn(
            {
                'year': self.project.financial_year,
                'amount': self.project.amount,
                'budget_phase': self.project.budget_phase
            },
            complete_expenditure
        )


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        return None


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):

    if args[0] == MAPIT_POINT_API_URL.format(25.312526, -27.515232):
        return MockResponse(
            {4288: {'name': 'Fake Province 1'}},
            200
        )
    elif args[0] == MAPIT_POINT_API_URL.format(24.312526, -26.515232):
        return MockResponse(
            {},
            200
        )
    elif args[0] == MAPIT_POINT_API_URL.format(29.45397, -31.45019):
        return MockResponse(
            {4288: {'name': 'Fake Province 3'}},
            200
        )
    elif args[0] == MAPIT_POINT_API_URL.format(25.443304, -33.399790):
        return MockResponse(
            {4288: {'name': 'Fake Province 4'}},
            200
        )
    elif args[0] == MAPIT_POINT_API_URL.format(15.443304, -30.399790):
        return MockResponse(
            {4288: {'name': 'Fake Province 5'}},
            200
        )
    return MockResponse(None, 404)


class ProvinceTestCase(TestCase):

    def setUp(self):
        self.test_coordinates_one = {
            'longitude': 25.312526,
            'latitude': -27.515232
        }
        self.test_coordinates_two = {
            'longitude': 24.312526,
            'latitude': -26.515232
        }

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_success_one_result(self, mock_get):
        province = InfrastructureProjectPart._get_province_from_coord(self.test_coordinates_one)
        self.assertEqual(province, 'Fake Province 1')

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_success_no_results(self, mock_get):
        province = InfrastructureProjectPart._get_province_from_coord(self.test_coordinates_two)
        self.assertEqual(province, None)

    def test_success_province_from_name(self):
        province = InfrastructureProjectPart._get_province_from_project_name('Eastern Cape: A New Test')
        self.assertEqual(province, 'Eastern Cape')


class MockDataset(mock.Mock):
    def get_resource(self, format):
        return {'id': 'fake id'}

    def get_url_path(self):
        return 'fake path'


empty_ckan_response = MockResponse(
            {
                'result': {
                    'records': []
                }
            },
            200
        )


class OverviewIntegrationTest(LiveServerTestCase):

    fixtures = [
        'test-infrastructure-pages-overview'
    ]

    def setUp(self):
        self.standard_fake_project = InfrastructureProjectPart.objects.filter(project_name='Standard fake project').first()

    @mock.patch('budgetportal.models.InfrastructureProjectPart.get_dataset', return_value=MockDataset())
    @mock.patch('requests.get', return_value=empty_ckan_response)
    def test_success_empty_projects(self, mock_dataset, mock_get):
        """ Test that it exists and that the correct years are linked. """
        InfrastructureProjectPart.objects.all().delete()
        c = Client()
        response = c.get('/infrastructure-projects')
        content = response.content
        self.assertTrue(content.find('fake path'))
        self.assertTrue(content.find('Infrastructure projects in South Africa for 2019-20'))
        self.assertTrue(content.find('Infrastructure Projects - vulekamali'))

    @mock.patch('budgetportal.models.InfrastructureProjectPart.get_dataset', return_value=MockDataset())
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_success_with_projects(self, mock_dataset, mock_get):
        """ Test that it exists and that the correct years are linked. """
        c = Client()
        response = c.get('/infrastructure-projects')
        content = response.content

        # First project
        self.assertTrue(content.find('Standard fake project'))
        self.assertTrue(content.find('Typical project description'))
        self.assertTrue(content.find('/infrastructure-projects/health-standard-fake-project'))
        self.assertTrue(content.find('fake type'))
        self.assertTrue(content.find('-31.45019'))
        self.assertTrue(content.find('29.45397'))
        self.assertTrue(content.find('standard fake investment'))
        self.assertTrue(content.find('5688808000.0'))
        self.assertTrue(content.find('Fake province 1'))
        self.assertTrue(content.find('/infrastructure-projects/health-standard-fake-project'))
        self.assertTrue(content.find('Fake stage'))
        self.assertTrue(content.find('9045389000'))

        for item in self.standard_fake_project.build_complete_expenditure():
            self.assertTrue(content.find(str(item)))

        # Second project
        self.assertTrue(content.find('Fake project 2'))
        self.assertTrue(content.find('-33.399790'))
        self.assertTrue(content.find('25.443304'))
        self.assertTrue(content.find('-30.399790'))
        self.assertTrue(content.find('15.443304'))
        self.assertTrue(content.find('Fake province 2'))
        self.assertTrue(content.find(' Fake province 3'))


class DetailIntegrationTest(LiveServerTestCase):

    fixtures = [
        'test-infrastructure-pages-detail'
    ]

    def setUp(self):
        self.project = InfrastructureProjectPart.objects.all().first()

    @mock.patch('budgetportal.models.InfrastructureProjectPart.get_dataset', return_value=None)
    def test_missing_dataset_returns_404(self, mock_dataset):
        c = Client()
        response = c.get('/infrastructure-projects/{}'.format(self.project.project_slug))
        self.assertEqual(response.status_code, 404)

    @mock.patch('budgetportal.models.InfrastructureProjectPart.get_dataset', return_value=MockDataset())
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_success_with_projects(self, mock_dataset, mock_get):
        """ Test that it exists and that the correct years are linked. """
        c = Client()
        response = c.get('/infrastructure-projects/{}'.format(
            self.project.project_slug))
        content = response.content

        self.assertTrue(content.find('fake path'))
        self.assertTrue(content.find(self.project.project_description))
        self.assertTrue(content.find(self.project.infrastructure_type))
        self.assertTrue(content.find(self.project.nature_of_investment))
        self.assertTrue(content.find('{} - vulekamali'.format(self.project.project_name)))
        self.assertTrue(content.find(str(self.project.calculate_projected_expenditure())))
        self.assertTrue(content.find('/infrastructure-projects/{}'.format(
            self.project.project_slug)))
        self.assertTrue(content.find(self.project.current_project_stage))
        self.assertTrue(content.find(str(self.project.total_project_cost)))
