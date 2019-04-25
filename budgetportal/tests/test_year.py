"""
Tests of models.FinancialYear
"""

from budgetportal.models import FinancialYear
from django.test import TestCase
from mock import Mock
import json

with open('budgetportal/tests/test_data/consolidated_treemap.json', 'r') as CONSOLIDATED_MOCK_DATA:
    CONSOLIDATED_MOCK_DATA = json.load(CONSOLIDATED_MOCK_DATA)


class ConsolidatedTreemapTestCase(TestCase):
    """ Unit tests for the consolidated treemap function(s) """

    def setUp(self):
        self.mock_data = CONSOLIDATED_MOCK_DATA
        self.year = FinancialYear.objects.create(slug="2019-20")

        mock_dataset = Mock()
        self.mock_openspending_api = Mock()
        self.mock_openspending_api.get_adjustment_kind_ref = Mock(return_value='adjustment_kind_ref')
        self.mock_openspending_api.aggregate = Mock(return_value={'cells': self.mock_data['complete']})
        self.mock_openspending_api.get_function_ref = Mock(return_value='function_group.function_group')
        self.mock_openspending_api.get_year_ref = Mock(return_value='function_group.function_group')
        self.mock_openspending_api.get_financial_year_ref = Mock(return_value="financial_year.financial_year")
        mock_dataset.get_openspending_api = Mock(return_value=self.mock_openspending_api)
        self.year.get_consolidated_expenditure_budget_dataset = Mock(return_value=mock_dataset)

    def test_no_cells_null_response(self):
        fake_result = {'cells': []}
        self.mock_openspending_api.aggregate = Mock(return_value=fake_result)
        result = self.year.get_consolidated_expenditure_treemap()
        self.assertEqual(result, None)

    def test_complete_data(self):
        result = self.year.get_consolidated_expenditure_treemap()
        data = result['data']
        self.assertEqual(len(data), 2)
        data_keys = data.keys()
        self.assertIn('items', data_keys)
        self.assertIn('total', data_keys)
        expenditure_keys = data['items'][0].keys()
        self.assertIn('name', expenditure_keys)
        self.assertIn('amount', expenditure_keys)
        self.assertIn('percentage', expenditure_keys)
        self.assertIn('id', expenditure_keys)
        self.assertIn('url', expenditure_keys)

