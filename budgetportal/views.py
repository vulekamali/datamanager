from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from models import FinancialYear
import yaml


def department_list(request, financial_year_id):
    context = {
        'financial_years': [],
    }

    selected_year = get_object_or_404(FinancialYear, slug=financial_year_id)

    for year in FinancialYear.objects.all().order_by('slug'):
        context['financial_years'].append({
            'id': year.slug,
            'is_selected': year == selected_year,
        })

    response_yaml = yaml.safe_dump(context, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')
