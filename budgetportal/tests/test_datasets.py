from django.test import TestCase
from mock import patch
from budgetportal.datasets import get_latest_cpi_resource


class TestGetLatestCPIResource(TestCase):
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
        with patch('budgetportal.models.ckan') as ckan_mock:
            ckan_mock.action.package_search.return_value = {
                'results': results}
            cpi_year, cpi_resource_id = get_latest_cpi_resource()
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

        with patch('budgetportal.models.ckan') as ckan_mock:
            ckan_mock.action.package_search.return_value = {'results': results}
            with self.assertRaises(AssertionError):
                cpi_year, cpi_resource_id = get_latest_cpi_resource()

            ckan_mock.action.package_search.assert_called_with(
                **self.cpi_cpi_query)
