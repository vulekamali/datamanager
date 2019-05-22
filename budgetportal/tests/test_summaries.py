"""
Tests of budgetportal.summaries
"""


from django.test import TestCase
import json
from mock import Mock, patch
from budgetportal.models import FinancialYear, Sphere, Government, Department
from budgetportal.summaries import (
    get_consolidated_expenditure_treemap,
    get_focus_area_preview,
)


with open('budgetportal/tests/test_data/consolidated_treemap.json', 'r') as f:
    CONSOLIDATED_MOCK_DATA = json.load(f)

with open('budgetportal/tests/test_data/test_year_focus_area_pages_provincial.json', 'r') as f:
    FOCUS_AREA_PROVINCIAL_MOCK_DATA = json.load(f)

with open('budgetportal/tests/test_data/test_year_focus_area_pages_national.json', 'r') as f:
    FOCUS_AREA_NATIONAL_MOCK_DATA = json.load(f)

with open('budgetportal/tests/test_data/test_year_focus_area_pages_national_subprogrammes.json', 'r') as f:
    FOCUS_AREA_NATIONAL_SUBPROGRAMMES_MOCK_DATA = json.load(f)


class ConsolidatedTreemapTestCase(TestCase):
    """ Unit tests for the consolidated treemap function(s) """

    def setUp(self):
        self.year = FinancialYear.objects.create(slug="2019-20")

        mock_dataset = Mock()
        self.mock_openspending_api = Mock()
        self.mock_openspending_api.get_adjustment_kind_ref = Mock(
            return_value='adjustment_kind_ref')
        self.mock_openspending_api.aggregate = Mock(
            return_value={'cells': CONSOLIDATED_MOCK_DATA['complete']})
        self.mock_openspending_api.get_function_ref = Mock(
            return_value='function_group.function_group')
        self.mock_openspending_api.get_year_ref = Mock(
            return_value='function_group.function_group')
        self.mock_openspending_api.get_financial_year_ref = Mock(
            return_value="financial_year.financial_year")
        mock_dataset.get_openspending_api = Mock(
            return_value=self.mock_openspending_api)
        self.get_consolidated_expenditure_budget_dataset = Mock(
            return_value=mock_dataset)

    def test_complete_data(self):
        result = get_consolidated_expenditure_treemap(self.year)
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


class FocusAreaPagesTestCase(TestCase):
    """ Integration test focus area page data generation """

    def setUp(self):
        self.year = FinancialYear.objects.create(slug="2019-20")
        self.year.save()
        national = Sphere(financial_year=self.year, name="national")
        national.save()
        provincial = Sphere(financial_year=self.year, name="provincial")
        provincial.save()
        southafrica = Government(sphere=national, name="South Africa")
        southafrica.save()
        province = Government(sphere=provincial, name="Test Province 1")
        province.save()
        Department(
            government=southafrica,
            name="TP1 National Test Dept 2",
            vote_number=1,
            is_vote_primary=True,
            intro="",
        ).save()
        Department(
            government=province,
            name="TP1 Provincial Test Dept 2",
            vote_number=1,
            is_vote_primary=True,
            intro="",
        ).save()

        self.mock_dataset = Mock()
        self.mock_openspending_api = Mock()
        self.mock_openspending_api.get_geo_ref = Mock(
            return_value='geo_source.government')
        self.mock_openspending_api.get_function_ref = Mock(
            return_value='function_group.function_group')
        self.mock_openspending_api.get_year_ref = Mock(
            return_value='function_group.function_group')
        self.mock_openspending_api.get_financial_year_ref = Mock(
            return_value="financial_year.financial_year")
        self.mock_openspending_api.get_department_name_ref = Mock(
            return_value="vote_number.department")
        self.mock_openspending_api.get_subprogramme_name_ref = Mock(
            return_value="subprogramme.subprogramme")
        self.mock_dataset.get_openspending_api = Mock(
            return_value=self.mock_openspending_api)

        def mock_get_focus_area_data(__, sphere):
            if sphere == "provincial":
                cells = FOCUS_AREA_PROVINCIAL_MOCK_DATA
            elif sphere == "national":
                cells = FOCUS_AREA_NATIONAL_MOCK_DATA
            return {'cells': cells}, self.mock_openspending_api

        self.mock_get_focus_area_data = mock_get_focus_area_data

    @patch('budgetportal.summaries.get_prov_eq_share')
    @patch('budgetportal.summaries.get_focus_area_data')
    def test_get_focus_area_preview(self, mock_get_focus_area_data, mock_get_prov_eq_share):
        mock_get_focus_area_data.side_effect = self.mock_get_focus_area_data
        mock_get_prov_eq_share.return_value = ('untested', 123)

        result = get_focus_area_preview(self.year)
        focus_areas = result['data']['items']
        fg1 = [f for f in focus_areas if f['slug'] == "test-fg-1"][0]
        fg2 = [f for f in focus_areas if f['slug'] == "test-fg-2"][0]

        self.assertEqual('Test FG 1', fg1['title'])
        self.assertEqual('Test FG 2', fg2['title'])

        self.assertEqual(6, len(fg1['national']['data']))
        self.assertEqual(6, len(fg1['provincial']['data']))

        nat_dept_data = [dept for dept in fg1['national']['data']
                         if dept['title'] == 'TP1 National Test Dept 2'][0]
        self.assertTrue(nat_dept_data['slug'] in nat_dept_data['url'])
        self.assertTrue('2019-20' in nat_dept_data['url'])

        prov_dept_data = [dept for dept in fg1['provincial']['data']
                          if dept['name'] == 'TP1 Provincial Test Dept 2'][0]
        self.assertTrue(prov_dept_data['slug'] in prov_dept_data['url'])
        self.assertTrue('2019-20' in prov_dept_data['url'])
