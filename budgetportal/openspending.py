import requests
import logging
from pprint import pformat

logger = logging.getLogger(__name__)

ACCOUNT_ID = 'b9d2af843f3a7ca223eea07fb608e62a'


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
        model_result.raise_for_status()
        self.model = model_result.json()['model']

    # These make assumptions about the OS Types we give Estimes of Expenditure
    # columns, and the level of which hierarchy they end up in.

    def get_programme_dimension(self):
        return self.model['hierarchies']['activity']['levels'][0]

    def get_department_dimension(self):
        return self.model['hierarchies']['administrative_classification']['levels'][0]

    def get_geo_dimension(self):
        return self.model['hierarchies']['geo_source']['levels'][0]

    def get_financial_year_dimension(self):
        return self.model['hierarchies']['date']['levels'][0]

    def get_function_dimension(self):
        return self.model['hierarchies']['functional_classification']['levels'][0]

    def aggregate(self, cuts=None, drilldowns=None):
        params = {
            'pagesize': 30
        }
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
        return aggregate_result.json()
