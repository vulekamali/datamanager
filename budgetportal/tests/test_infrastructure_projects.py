from django.test import TestCase

from budgetportal.models import InfrastructureProject


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
