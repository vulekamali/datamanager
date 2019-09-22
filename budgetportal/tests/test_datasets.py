import json

from django.conf import settings
from django.test import TestCase, Client
from mock import patch

from budgetportal.datasets import Dataset

with open('budgetportal/tests/test_data/test_contributed_datasets_list.json', 'r') as f:
    CONTRIBUTED_DATASETS_LIST_MOCK_DATA = json.load(f)
with open('budgetportal/tests/test_data/test_contributed_dataset.json', 'r') as f:
    CONTRIBUTED_DATASET_MOCK_DATA = json.load(f)


class TestDataset(TestCase):
    def setUp(self):
        self.cpi_cpi_query = {
            'q': '',
            'fq': ''.join([
                '+organization:"national-treasury"',
                '+groups:"cpi-inflation"',
            ]),
            'rows': 1000,
        }

    def test_get_latest_cpi_resource(self):
        results = [
            {
                'financial_year': [u'2020-21'],
                'resources': [{'format': u'CSV',
                               'id': u'0c173948-9674-4ca9-aec6-f144bde5cc1e'}]},
            {
                'financial_year': [u'2018-19'],
                'resources': [
                    {'format': u'XLSX',
                               'id': u'd1f96183-83e5-4ff1-87f5-c58e279b6f63'},
                    {'format': u'CSV', 'id': u'5b315ff0-55e9-4ba8-b88c-2d70093bfe9d'}
                ]}
        ]
        with patch('budgetportal.datasets.ckan') as ckan_mock:
            ckan_mock.action.package_search.return_value = {
                'results': results}
            cpi_year, cpi_resource_id = Dataset.get_latest_cpi_resource()
            ckan_mock.action.package_search.assert_called_with(
                **self.cpi_cpi_query)
            self.assertEqual('2020-21', cpi_year)
            self.assertEqual(
                '0c173948-9674-4ca9-aec6-f144bde5cc1e', cpi_resource_id)

    def test_get_latest_cpi_resource_multiple_financial_year_values(self):
        results = [
            {
                'financial_year': [u'2019-20', '2020-21'],
                'resources': [{'format': u'CSV',
                               'id': u'0c173948-9674-4ca9-aec6-f144bde5cc1e'}]},
        ]

        with patch('budgetportal.datasets.ckan') as ckan_mock:
            ckan_mock.action.package_search.return_value = {'results': results}
            with self.assertRaises(AssertionError):
                cpi_year, cpi_resource_id = Dataset.get_latest_cpi_resource()

            ckan_mock.action.package_search.assert_called_with(
                **self.cpi_cpi_query)

    def test_contributed_datasets_list(self):
        """Test that it loads and that some text is present"""
        c = Client()
        with patch('budgetportal.datasets.ckan') as ckan_mock:
            ckan_mock.action.package_search.return_value = CONTRIBUTED_DATASETS_LIST_MOCK_DATA
            response = c.get('/datasets/contributed')
            content = response.content
            self.assertTrue(content.find("Education Budget Brief 2019/20"))
            self.assertTrue(content.find("People's Guide to the Adjusted Budget 2018/19"))
            self.assertTrue(content.find("db3ab7ec-9f62-46a6-94f9-e43f3c8536a5"))
            self.assertTrue(content.find("9c7af295-9362-44ea-9731-b95bb1ea89d3"))

    @patch('budgetportal.datasets.ckan.action.organization_show', return_value=CONTRIBUTED_DATASET_MOCK_DATA)
    @patch('budgetportal.datasets.ckan.action.package_show', return_value=CONTRIBUTED_DATASET_MOCK_DATA)
    def test_contributed_dataset(self, mock_package_show, mock_organization_show):
        """Test that it loads and that some text is present"""
        c = Client()
        response = c.get('/datasets/contributed/people-s-guide-to-the-adjusted-budget-2018-19')
        content = response.content
        self.assertTrue(content.find("People's Guide to the Adjusted Budget 2018/19"))
        self.assertTrue(content.find("9c7af295-9362-44ea-9731-b95bb1ea89d3"))
        self.assertTrue(content.find("test-url"))
        self.assertTrue(content.find("basic-organization-slug"))
