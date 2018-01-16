from django.http import HttpResponse
from models import FinancialYear
import yaml


def department_list(request, financial_year_id):
    context = {
        'financial_years': [],
        'selected_financial_year': financial_year_id,
    }

    selected_year = None
    for year in FinancialYear.objects.order_by('slug'):
        is_selected = year.slug == financial_year_id
        if is_selected:
            selected_year = year
        context['financial_years'].append({
            'id': year.slug,
            'is_selected': is_selected,
            'closest_match': {
                'is_exact_match': True,
                'name': 'Departments',
                'slug': 'departments',
                'organisational_unit': 'financial_year',
                'url_path': "%s/departments" % year.slug,
            },
        })

    for sphere_name in ('national', 'provincial'):
        context[sphere_name] = []
        for government in selected_year.spheres.filter(slug=sphere_name).first().governments.all():
            departments = []
            for department in government.departments.all():
                departments.append({
                    'name': department.name,
                    'slug': str(department.slug),
                    'vote_number': department.vote_number,
                    'url_path': department.get_url_path(),
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
    department = None

    years = list(FinancialYear.objects.order_by('slug'))
    for year in years:
        if year.slug == financial_year_id:
            selected_year = year
            sphere = selected_year.spheres.filter(slug=sphere_slug).first()
            government = sphere.governments.filter(slug=government_slug).first()
            department = government.departments.filter(slug=department_slug).first()

    financial_years_context = []
    for year in years:
        closest_match, closest_is_exact = year.get_closest_match(department)
        financial_years_context.append({
            'id': year.slug,
            'is_selected': year.slug == financial_year_id,
            'closest_match': {
                'name': closest_match.name,
                'slug': str(closest_match.slug),
                'url_path': closest_match.get_url_path(),
                'organisational_unit': closest_match.organisational_unit,
                'is_exact_match': closest_is_exact,
            },
        })
    context = {
        'name': department.name,
        'slug': str(department.slug),
        'vote_number': department.vote_number,
        'government': {
            'name': department.government.name,
            'slug': str(department.government.slug),
        },
        'sphere': {
            'name': department.government.sphere.name,
            'sphere': department.government.sphere.slug,
        },
        'selected_financial_year': financial_year_id,
        'financial_years': financial_years_context,
        'intro': department.intro,
        'resources': department.get_resources(),
        'programmes': [{'name': p.name} for p in department.programmes.order_by('programme_number')],
    }

    response_yaml = yaml.safe_dump(context, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')
