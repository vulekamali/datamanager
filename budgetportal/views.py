from django.http import HttpResponse
from models import FinancialYear
import yaml


def department_list(request, financial_year):
    context = {
        'financial_years': [],
        'national': [],
    }
    for year in FinancialYear.get_all():
        context['financial_years'].append(year.id)

    response_yaml = yaml.safe_dump(context, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')
