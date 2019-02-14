from django.test import TestCase

from budgetportal.models import InfrastructureProject


class ProjectedExpenditureTestCase(TestCase):
    """ Unit tests for get_projected_expenditure function """

    def setUp(self):
        self.fake_records = [
            {'Financial Year': 2016, 'Amount': 100},
            {'Financial Year': 2017, 'Amount': 100},
            {'Financial Year': 2018, 'Amount': 100},
            {'Financial Year': 2019, 'Amount': 100},
            {'Financial Year': 2020, 'Amount': 100},
            {'Financial Year': 2021, 'Amount': 100}
        ]
        self.project = InfrastructureProject()

    def test_success(self):
        self.project.records = self.fake_records
        projected_expenditure = self.project.get_projected_expenditure()
        self.assertEqual(projected_expenditure, 300)

    def test_empty_records_returns_zero(self):
        self.project.records = []
        projected_expenditure = self.project.get_projected_expenditure()
        self.assertEqual(projected_expenditure, 0)


class CleanedCoordinatesTestCase(TestCase):
    """ Unit tests for get_cleaned_coordinates function """

    def setUp(self):
        self.project = InfrastructureProject()

    def test_standard_format(self):
        self.project.gps_codes = '-26.378582,27.654933'
        coords = self.project.get_cleaned_coordinates()
        self.assertEqual(coords, [
            {
                'latitude': -26.378582,
                'longitude': 27.654933
            }
        ])

    def test_multiple_coordinates(self):
        self.project.gps_codes = '-26.378582,27.654933 and -22.111222,23.333444'
        coords = self.project.get_cleaned_coordinates()
        self.assertEqual(coords, [
            {
                'latitude': -26.378582,
                'longitude': 27.654933
            },
            {
                'latitude': -22.111222,
                'longitude': 23.333444
            }
        ])

    def test_invalid_value(self):
        self.project.name = 'fake project'  # needed for exception logging due to invalid value
        self.project.gps_codes = '  fake invalid value  with    funky spacing?'
        coords = self.project.get_cleaned_coordinates()
        self.assertEqual(coords, [])


class ExpenditureTestCase(TestCase):
    """ Unit tests for the get_provinces function """

    def setUp(self):
        self.project = InfrastructureProject()
        self.project.records = [
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

    def test_success(self):
        expenditure = self.project.get_expenditure()
        self.assertEqual(expenditure, [
            {
                'year': 2030,
                'amount': 123.0,
                'budget_phase': 'fake budget phase'
            },
            {
                'year': 2031,
                'amount': 1000.0,
                'budget_phase': 'fake budget phase 2'
            }
        ])

