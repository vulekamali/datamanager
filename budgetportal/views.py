from django.http import HttpResponse, Http404
from models import FinancialYear
import yaml


def department_list(request, financial_year_id):
    context = {
        'financial_years': [],
    }

    selected_year = None
    for year in FinancialYear.get_all():
        is_selected = year.id == financial_year_id
        if is_selected:
            selected_year = year
        context['financial_years'].append({
            'id': year.id,
            'is_selected': is_selected,
        })

    response_yaml = yaml.safe_dump(context, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')
