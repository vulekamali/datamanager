import requests
from requests.exceptions import HTTPError, ConnectionError


def get_budget_resources(year, dept_name):
    """
    Fetch budget totals for a department programs.
    return dict
    """
    params = {
        'cut': ('date_2.financial_year:{}|'
                'administrative_classification_2.department:"{}"')
        .format(year, dept_name),
        'drilldown': ('activity_programme_number.programme_number|'
                      'activity_programme_number.programme'),
        'order': 'activity_programme_number.programme_number:asc',
        'pagesize': 30
    }
    url = ('https://openspending.org/api/3/cubes/'
           'fb2fa9b200eb3e56facc4c287002fc4d:'
           'estimates-of-national-expenditure-south-africa-2017-18/'
           'aggregate')
    try:
        result = requests.get(url, params=params)
        if result.status_code == 200:
            # maybe check for json status as 'ok'
            return result.json()
    except (HTTPError, ConnectionError) as e:
        return None
    return None
