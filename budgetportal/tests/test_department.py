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
        self.mock_openspending_api.get_programme_name_ref = Mock
        self.mock_openspending_api.get_department_name_ref = Mock(return_value='department_name_ref')
        self.mock_openspending_api.get_financial_year_ref = Mock(return_value="financial_year.financial_year")
        self.mock_openspending_api.aggregate = Mock(return_value={'cells': [{'value.sum': 1, '_count': 0}]})
        self.mock_openspending_api.filter_dept = Mock(return_value={'cells': []})
        self.mock_openspending_api.filter_by_ref_exclusion = Mock
        self.mock_openspending_api.aggregate_by_three_ref = Mock(return_value=test_cells_data_complete)
        self.mock_openspending_api.aggregate_url = Mock
        mock_dataset.get_openspending_api = Mock(return_value=self.mock_openspending_api)
        self.department.get_expenditure_time_series_dataset = Mock(return_value=mock_dataset)
        self.department.get_financial_year = Mock(return_value=year)

    def test_no_cells_null_response(self):
        self.mock_openspending_api.aggregate_by_three_ref = Mock(return_value=[])
        result = self.department.get_expenditure_time_series_summary()
        self.assertEqual(result, None)

    def test_complete_data_no_notices(self):
        result = self.department.get_expenditure_time_series_summary()
        self.assertEqual(result['notices'], [])

    def test_missing_data_not_published(self):
        """ Here we feed an incomplete set of cells and expect it to tell us that 2018 data has not been published """
        self.mock_openspending_api.aggregate = Mock(return_value={'cells': [{'value.sum': 0, '_count': 0}]})
        self.mock_openspending_api.aggregate_by_three_ref = Mock(return_value=test_cells_data_missing_2018)
        result = self.department.get_expenditure_time_series_summary()
        self.assertEqual(result['notices'], ['Please note that the data for 2018 has not been published on vulekamali.'])

    def test_missing_data_dept_did_not_exist(self):
        """ Here we feed an incomplete set of cells and expect it to tell us that the department did not exist
        (removed 2018 data) """
        self.mock_openspending_api.aggregate = Mock(return_value={'cells': [{'value.sum': 1, '_count': 0}]})
        self.mock_openspending_api.aggregate_by_three_ref = Mock(return_value=test_cells_data_missing_2018)
        result = self.department.get_expenditure_time_series_summary()
        self.assertEqual(result['notices'], ['This department did not exist for some years displayed.'])


test_cells_data_missing_2018 = [{
    'budget_phase.budget_phase': 'Adjusted appropriation',
    'vote_number.department': 'National Treasury', '_count': 557,
    'financial_year.financial_year': 2015, 'value.sum': 28726061000
}, {
    'budget_phase.budget_phase': 'Audit Outcome',
    'vote_number.department': 'National Treasury', '_count': 558,
    'financial_year.financial_year': 2015, 'value.sum': 28690816280
}, {
    'budget_phase.budget_phase': 'Final Appropriation',
    'vote_number.department': 'National Treasury', '_count': 566,
    'financial_year.financial_year': 2015, 'value.sum': 29005061000
}, {
    'budget_phase.budget_phase': 'Main appropriation',
    'vote_number.department': 'National Treasury', '_count': 685,
    'financial_year.financial_year': 2015, 'value.sum': 26957304000.0
}, {
    'budget_phase.budget_phase': 'Adjusted appropriation',
    'vote_number.department': 'National Treasury', '_count': 565,
    'financial_year.financial_year': 2016, 'value.sum': 28471417000
}, {
    'budget_phase.budget_phase': 'Audit Outcome',
    'vote_number.department': 'National Treasury', '_count': 155,
    'financial_year.financial_year': 2016, 'value.sum': 28199783365
}, {
    'budget_phase.budget_phase': 'Final Appropriation',
    'vote_number.department': 'National Treasury', '_count': 157,
    'financial_year.financial_year': 2016, 'value.sum': 28471416900
}, {
    'budget_phase.budget_phase': 'Main appropriation',
    'vote_number.department': 'National Treasury', '_count': 684,
    'financial_year.financial_year': 2016, 'value.sum': 28471417000.0
}, {
    'budget_phase.budget_phase': 'Adjusted appropriation',
    'vote_number.department': 'National Treasury', '_count': 568,
    'financial_year.financial_year': 2017, 'value.sum': 40584306000
}, {
    'budget_phase.budget_phase': 'Audit Outcome',
    'vote_number.department': 'National Treasury', '_count': 503,
    'financial_year.financial_year': 2017, 'value.sum': 39792071170
}, {
    'budget_phase.budget_phase': 'Final Appropriation',
    'vote_number.department': 'National Treasury', '_count': 559,
    'financial_year.financial_year': 2017, 'value.sum': 40484306000
}, {
    'budget_phase.budget_phase': 'Main appropriation',
    'vote_number.department': 'National Treasury', '_count': 820,
    'financial_year.financial_year': 2017, 'value.sum': 30799220000.0
}]

test_cells_only_2018 = [{
    'budget_phase.budget_phase': 'Adjusted appropriation',
    'vote_number.department': 'National Treasury', '_count': 536,
    'financial_year.financial_year': 2018, 'value.sum': 29710233000
}, {
   'budget_phase.budget_phase': 'Main appropriation',
   'vote_number.department': 'National Treasury', '_count': 882,
   'financial_year.financial_year': 2018, 'value.sum': 29358390000.0
}]


test_cells_data_complete = test_cells_data_missing_2018 + test_cells_only_2018
