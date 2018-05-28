"""
Abstracts away some of the mechanics of querying OpenSpending and some of the
conventions of how we name fields in our Fiscal Data Packages.
"""
from django.conf import settings
from pprint import pformat
import logging
import random
import requests

logger = logging.getLogger(__name__)

ACCOUNT_ID = 'b9d2af843f3a7ca223eea07fb608e62a'
PAGE_SIZE = 300

class EstimatesOfExpenditure():
    def __init__(self, financial_year_slug, sphere_slug):
        self.sphere_slug = sphere_slug
        dataset_id = 'estimates-of-%s-expenditure-south-africa-%s' % (
            sphere_slug,
            financial_year_slug,
        )
        self.cube_url = ('https://openspending.org/api/3/cubes/'
                         '{}:{}/').format(ACCOUNT_ID, dataset_id)
        model_url = self.cube_url + 'model/'
        model_result = requests.get(model_url)
        logger.info(
            "request to %s took %dms",
            model_url,
            model_result.elapsed.microseconds / 1000
        )
        if model_result.status_code == 404:
            logger.info("%s not found (404)" % model_result.url)
            dataset_id = ('estimates_of_%s_expenditure_of_south_africa_%s' % (
                sphere_slug,
                financial_year_slug,
            )).replace('-', '_')
            self.cube_url = ('https://openspending.org/api/3/cubes/'
                             '{}:{}/').format(ACCOUNT_ID, dataset_id)
            model_url = self.cube_url + 'model/'
            model_result = requests.get(model_url)
            logger.info(
                "request to %s took %dms",
                model_url,
                model_result.elapsed.microseconds / 1000
            )

        model_result.raise_for_status()
        self.model = model_result.json()['model']

    # These make assumptions about the OS Types we give Estimes of Expenditure
    # columns, and the level of which hierarchy they end up in.

    def get_programme_name_ref(self):
        return self.get_programme_dimension() + '.programme'

    def get_programme_number_ref(self):
        return self.get_programme_dimension() + '.programme_number'

    def get_programme_dimension(self):
        return self.model['hierarchies']['activity']['levels'][0]

    def get_department_name_ref(self):
        return self.get_department_dimension() + '.department'

    def get_vote_number_ref(self):
        return self.get_department_dimension() + '.vote_number'

    def get_department_dimension(self):
        return self.model['hierarchies']['administrative_classification']['levels'][0]

    def get_geo_ref(self):
        return self.get_geo_dimension() + '.government'

    def get_geo_dimension(self):
        return self.model['hierarchies']['geo_source']['levels'][0]

    def get_financial_year_ref(self):
        return self.get_financial_year_dimension() + '.financial_year'

    def get_financial_year_dimension(self):
        return self.model['hierarchies']['date']['levels'][0]

    def get_function_ref(self):
        return self.get_function_dimension() + '.government_function'

    def get_function_dimension(self):
        return self.model['hierarchies']['functional_classification']['levels'][0]

    def get_phase_ref(self):
        return self.get_phase_dimension() + '.budget_phase'

    def get_phase_dimension(self):
        return self.model['hierarchies']['phase']['levels'][0]

    def aggregate(self, cuts=None, drilldowns=None):
        params = {
            'pagesize': PAGE_SIZE,
        }
        if settings.BUST_OPENSPENDING_CACHE:
            params['cache_bust'] = random.randint(1, 1000000)

        if cuts is not None:
            params['cut'] = "|".join(cuts)
        if drilldowns is not None:
            params['drilldown'] = "|".join(drilldowns)
        aggregate_url = self.cube_url + 'aggregate/'
        aggregate_result = requests.get(aggregate_url, params=params)
        logger.info(
            "request %s with query %r took %dms",
            aggregate_result.url,
            pformat(params),
            aggregate_result.elapsed.microseconds / 1000
        )
        aggregate_result.raise_for_status()
        if aggregate_result.json()['total_cell_count'] > PAGE_SIZE:
            raise Exception("More cells than expected - perhaps we should start paging")
        return aggregate_result.json()
