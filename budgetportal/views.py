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
            'closest_match': {
                'is_exact_match': True,
                'name': 'Departments',
                'slug': 'departments',
                'organisational_unit': 'financial_year',
                'url_path': "%s/departments" % year.id,
            },
        })

    for sphere_name in ('national', 'provincial'):
        context[sphere_name] = []
        for government in selected_year.get_sphere(sphere_name).governments:
            departments = []
            for department in government.departments:
                departments.append({
                    'name': department.name,
                    'slug': str(department.slug),
                    'vote_number': department.vote_number,
                })
            departments = sorted(departments, key=lambda d: d['vote_number'])
            context[sphere_name].append({
                'name': government.name,
                'slug': str(government.slug),
                'departments': departments,
            })

    response_yaml = yaml.safe_dump(context, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def department(request, financial_year_id, sphere_slug, government_slug, department_slug):
    context = {
    }

    financial_years_context = []

    department = None
    years = list(FinancialYear.get_all())
    for year in years:
        if year.id == financial_year_id:
            selected_year = year
            sphere = selected_year.get_sphere(sphere_slug)
            government = sphere.get_government_by_slug(government_slug)
            department = government.get_department_by_slug(department_slug)

    for year in years:
        closest_match, closest_is_exact = year.get_closest_match(department)
        financial_years_context.append({
            'id': year.id,
            'is_selected': year.id == financial_year_id,
            'closest_match': {
                'name': closest_match.name,
                'slug': str(closest_match.slug),
                'url_path': closest_match.get_url_path(),
                'organisational_unit': closest_match.organisational_unit,
                'is_exact_match': closest_is_exact,
            },
        })
    context['financial_years'] = financial_years_context

    response_yaml = yaml.safe_dump(context, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')
