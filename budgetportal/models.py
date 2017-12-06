from django.utils.text import slugify
import requests
from requests.adapters import HTTPAdapter
from django.conf import settings

ckan = settings.CKAN


class FinancialYear():
    organisational_unit = 'financial_year'

    class Meta:
        managed = False

    def __init__(self, id):
        self.id = id

    def get_url_path(self):
        return "/%s" % self.id

    @staticmethod
    def get_all():
        response = ckan.action.package_search(**{
            'q':'', 'facet.field':'["vocab_financial_years"]', 'rows':0})
        years_facet = response['search_facets']['vocab_financial_years']['items']
        years_facet.sort(key=lambda f: f['name'])
        for year in years_facet:
            yield FinancialYear(year['name'])
