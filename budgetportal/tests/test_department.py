"""
Tests of models.Department
"""

from budgetportal.models import (
    FinancialYear,
    Sphere,
    Government,
    Department,
)
from budgetportal import models
from django.test import TestCase
from mock import Mock
import json

class AdjustedBudgetMissingTestCase(TestCase):
    """Unit tests of adjusted budget data summary for a department"""

    def setUp(self):
        year = FinancialYear(slug="2030-31")
        sphere = Sphere(financial_year=year, name="A sphere")
        government = Government(sphere=sphere, name="A government")
        self.department = Department(
            government=government,
            name="Fake",
            vote_number=1,
            is_vote_primary=True,
            intro="",
        )
        self.department.get_adjusted_estimates_expenditure_dataset = Mock(return_value=None)

    def test_missing_dataset(self):
        self.assertEqual(self.department.get_adjusted_budget_summary(), None)


class AdjustedBudgetOpenSpendingMissingTestCase(TestCase):
    """Unit tests of adjusted budget data summary for a department"""

    def setUp(self):
        year = FinancialYear(slug="2030-31")
        sphere = Sphere(financial_year=year, name="A sphere")
        government = Government(sphere=sphere, name="A government")
        self.department = Department(
            government=government,
            name="Fake",
            vote_number=1,
            is_vote_primary=True,
            intro="",
        )
        mock_dataset = Mock()
        mock_dataset.get_openspending_api = Mock(return_value=None)
        self.department.get_adjusted_estimates_expenditure_dataset = Mock(return_value=mock_dataset)

    def test_missing_openspending_dataset(self):
        self.assertEqual(self.department.get_adjusted_budget_summary(), None)


class AdjustedBudgetTestCase(TestCase):
    """Unit tests of adjusted budget data summary for a department"""

    def setUp(self):
        year = FinancialYear(slug="2030-31")
        sphere = Sphere(financial_year=year, name="A sphere")
        government = Government(sphere=sphere, name="A government")
        self.department = Department(
            government=government,
            name="Fake",
            vote_number=1,
            is_vote_primary=True,
            intro="",
        )
        mock_dataset = Mock()
        mock_openspending_api = Mock()
        self.mock_openspending_api = mock_openspending_api
        mock_openspending_api.get_adjustment_kind_ref = Mock
        mock_openspending_api.get_phase_ref = Mock
        mock_openspending_api.get_programme_name_ref = Mock
        mock_openspending_api.get_department_name_ref = Mock(return_value='department_name_ref')
        mock_openspending_api.get_financial_year_ref = Mock(return_value="financial_year_ref")
        mock_openspending_api.aggregate = Mock
        mock_openspending_api.filter_dept = Mock(return_value={'cells': []})
        mock_openspending_api.filter_by_ref_exclusion = Mock
        mock_openspending_api.aggregate_by_ref = Mock
        mock_openspending_api.aggregate_url = Mock
        mock_dataset.get_openspending_api = Mock(return_value=mock_openspending_api)
        self.department.get_adjusted_estimates_expenditure_dataset = Mock(return_value=mock_dataset)
        self.department.get_financial_year = Mock(return_value=year)
        self.department._get_adjustments_by_econ_class = Mock(return_value=Mock())
        self.department._get_adjustments_by_programme = Mock(return_value=Mock())
        self.department._get_adjustments_by_type = Mock(return_value=Mock())
        self.department._get_budget_virements = Mock(return_value=Mock())
        self.department._get_budget_special_appropriations = Mock(return_value=Mock())
        self.department._get_budget_direct_charges = Mock(return_value=Mock())
        models.csv_url = Mock(return_value=Mock())

    def test_no_adjustment(self):
        self.department._get_total_budget_adjustment = Mock(return_value=(123, 0))
        result = self.department.get_adjusted_budget_summary()
        self.assertEqual(result['total_change']['amount'], 0)
        self.assertEqual(result['total_change']['percentage'], 0)

    def test_adjustment(self):
        self.department._get_total_budget_adjustment = Mock(return_value=(100, 11))
        result = self.department.get_adjusted_budget_summary()
        self.assertEqual(result['total_change']['amount'], 11)
        self.assertEqual(result['total_change']['percentage'], 11)


class BudgetedAndActualExpenditureSummaryTestCase(TestCase):
    """Unit tests of budgeted and actual expenditure summary for a department"""

    def setUp(self):
        with open('budgetportal/tests/test_data/budget_and_actual.json', 'r') as mock_data:
            self.mock_data = json.load(mock_data)
        year = FinancialYear(slug="2018-19")
        sphere = Sphere(financial_year=year, name="A sphere")
        government = Government(sphere=sphere, name="A government")
        self.department = Department(
            government=government,
            name="Fake",
            vote_number=1,
            is_vote_primary=True,
            intro="",
        )
        mock_dataset = Mock()
        self.mock_openspending_api = Mock()
        self.mock_openspending_api.get_adjustment_kind_ref = Mock(return_value='adjustment_kind_ref')
        self.mock_openspending_api.get_phase_ref = Mock(return_value='budget_phase.budget_phase')
        self.mock_openspending_api.get_programme_name_ref = Mock(return_value='programme_number.programme')
        self.mock_openspending_api.get_department_name_ref = Mock(return_value='department_name_ref')
        self.mock_openspending_api.get_financial_year_ref = Mock(return_value="financial_year.financial_year")
        self.mock_openspending_api.aggregate = Mock(return_value={'cells': [{'value.sum': 1, '_count': 0}]})
        self.mock_openspending_api.filter_dept = Mock(return_value={'cells': self.mock_data['program_test_cells_complete']})
        self.mock_openspending_api.aggregate_url = Mock
        mock_dataset.get_openspending_api = Mock(return_value=self.mock_openspending_api)
        self.department.get_expenditure_time_series_dataset = Mock(return_value=mock_dataset)
        self.department.get_financial_year = Mock(return_value=year)

    def test_no_cells_null_response(self):
        self.mock_openspending_api.filter_dept = Mock(return_value={'cells': []})
        result = self.department.get_expenditure_time_series_by_programme()
        self.assertEqual(result, None)

    def test_complete_data_no_notices(self):
        result = self.department.get_expenditure_time_series_by_programme()
        self.assertEqual(result['notices'], [])

    def test_missing_data_prog_did_not_exist(self):
        """ Here we feed an incomplete set of cells and expect it to tell us that the department did not exist
        (removed 2018 data) """
        self.mock_openspending_api.aggregate = Mock(return_value={'cells': [{'value.sum': 1, '_count': 0}]})
        self.mock_openspending_api.filter_dept = Mock(return_value={'cells': self.mock_data['program_test_cells_missing_2018_revenue_admin']})
        result = self.department.get_expenditure_time_series_by_programme()
        self.assertEqual(result['notices'], ['One or more programmes did not exist for some years displayed.'])


