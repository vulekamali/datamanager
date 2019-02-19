import mock
import yaml
from django.test import TestCase, LiveServerTestCase, Client
import requests

from budgetportal import settings
from budgetportal.models import InfrastructureProject, MAPIT_POINT_API_URL, CKAN_DATASTORE_URL


class ProjectedExpenditureTestCase(TestCase):
    """ Unit tests for get_projected_expenditure function """

    def setUp(self):
        self.fake_valid_records = [
            {'Budget Phase': 'test phase one', 'Amount': 100},
            {'Budget Phase': 'test phase one', 'Amount': 100},
            {'Budget Phase': 'test phase two', 'Amount': 100},
            {'Budget Phase': 'MTEF', 'Amount': 200},
            {'Budget Phase': 'MTEF', 'Amount': 200},
            {'Budget Phase': 'MTEF', 'Amount': 200},
        ]

    def test_success(self):
        projected_expenditure = InfrastructureProject._calculate_projected_expenditure(
            self.fake_valid_records
        )
        self.assertEqual(projected_expenditure, 600)

    def test_empty_records_returns_zero(self):
        projected_expenditure = InfrastructureProject._calculate_projected_expenditure([])
        self.assertEqual(projected_expenditure, 0)

    def test_string_raises_type_error(self):
        self.assertRaises(
            TypeError,
            InfrastructureProject._calculate_projected_expenditure,
            'test string raises exception'
        )


class CoordinatesTestCase(TestCase):
    """ Unit tests for parsing coordinates """

    def test_success_simple_format(self):
        raw_coord_string = '-26.378582,27.654933'
        cleaned_coord_object = InfrastructureProject._parse_coordinate(
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
            InfrastructureProject._parse_coordinate,
            invalid_coordinate
        )

    def test_failure_list_raises_type_error(self):
        invalid_coordinate = [25, 23]
        self.assertRaises(
            TypeError,
            InfrastructureProject._parse_coordinate,
            invalid_coordinate
        )

    def test_success_multiple_coordinates(self):
        raw_coordinate_string = '-26.378582,27.654933 and -22.111222,23.333444'
        coords = InfrastructureProject._clean_coordinates(raw_coordinate_string)
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
        coords = InfrastructureProject._clean_coordinates(raw_coordinate_string)
        self.assertEqual(coords, [])


class ExpenditureTestCase(TestCase):
    """ Unit tests for expenditure functions """

    def setUp(self):
        self.fake_valid_records = [
            {
                'Financial Year': 2030,
                'Budget Phase': 'fake budget phase',
                'Amount': 123
            },
            {
                'Financial Year': 2031,
                'Budget Phase': 'fake budget phase 2',
                'Amount': 1000
            },
        ]
        self.expected_output_2030 = {
            'year': 2030,
            'amount': 123.0,
            'budget_phase': 'fake budget phase'
        }
        self.expected_output_2031 = {
            'year': 2031,
            'amount': 1000,
            'budget_phase': 'fake budget phase 2'
        }

    def test_success_build_expenditure_item(self):
        expenditure_item = InfrastructureProject._build_expenditure_item(self.fake_valid_records[0])
        self.assertEqual(
            expenditure_item,
            self.expected_output_2030
        )

    def test_failure_missing_fields(self):
        self.assertRaises(
            KeyError,
            InfrastructureProject._build_expenditure_item,
            {
                'Not enough keys': 'to parse successfully'
            }
        )

    def test_success_build_complete_expenditure(self):
        complete_expenditure = InfrastructureProject._build_complete_expenditure(self.fake_valid_records)
        self.assertIn(
            self.expected_output_2030,
            complete_expenditure
        )
        self.assertIn(
            self.expected_output_2031,
            complete_expenditure
        )


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            return None

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

    return MockResponse(None, 404)


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        return None


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
        province = InfrastructureProject._get_province_from_coord(self.test_coordinates_one)
        self.assertEqual(province, 'Fake Province 1')

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_success_no_results(self, mock_get):
        province = InfrastructureProject._get_province_from_coord(self.test_coordinates_two)
        self.assertEqual(province, None)


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

populated_ckan_response = MockResponse(
            {
                'result': {
                    'records': []
                }
            },
            200
        )


class OverviewIntegrationTest(LiveServerTestCase):

    @mock.patch('budgetportal.models.InfrastructureProject.get_dataset', return_value=None)
    def test_missing_dataset_returns_404(self, mock_dataset):
        c = Client()
        response = c.get('/infrastructure-projects.yaml')
        self.assertEqual(response.status_code, 404)

    @mock.patch('budgetportal.models.InfrastructureProject.get_dataset', return_value=MockDataset())
    @mock.patch('requests.get', return_value=empty_ckan_response)
    def test_success_empty_projects(self, mock_dataset, mock_get):
        """ Test that it exists and that the correct years are linked. """
        c = Client()
        response = c.get('/infrastructure-projects.yaml')
        content = yaml.load(response.content)
        self.assertEqual(content['projects'], [])
        self.assertEqual(content['dataset_url'], 'fake path')
        self.assertEqual(content['description'], 'Infrastructure projects in South Africa for 2019-20')
        self.assertEqual(content['selected_tab'], 'infrastructure-projects')
        self.assertEqual(content['slug'], 'infrastructure-projects')
        self.assertEqual(content['title'], 'Infrastructure Projects - vulekamali')

    @mock.patch('budgetportal.models.InfrastructureProject.get_dataset', return_value=MockDataset())
    @mock.patch('requests.get', return_value=populated_ckan_response)
    def test_success_with_projects(self, mock_dataset, mock_get):
        """ Test that it exists and that the correct years are linked. """
        c = Client()
        response = c.get('/infrastructure-projects.yaml')
        content = yaml.load(response.content)
        self.assertEqual(content.projects, [])
        self.assertEqual(content.dataset_url, 'fake path')
        self.assertEqual(content.description, 'Infrastructure projects in South Africa for 2019-20')
        self.assertEqual(content.selected_tab, 'infrastructure-projects')
        self.assertEqual(content.slug, 'infrastructure-projects')
        self.assertEqual(content.title, 'Infrastructure Projects - vulekamali')