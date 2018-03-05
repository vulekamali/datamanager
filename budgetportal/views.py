from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from models import FinancialYear, Dataset
import yaml

from . import revenue


def home(request, financial_year_id):
    """
    Generate and show national budget revenue
    """
    year = get_object_or_404(FinancialYear, slug=financial_year_id)
    revenue_data = year.get_budget_revenue()

    context = {
        'selected_financial_year': financial_year_id,
        'revenue': revenue.sort_categories(revenue_data),
        'organisational_unit': 'financial_year',
        'slug': financial_year_id,
        'url_path': year.get_url_path(),
        'financial_years': [],
    }
    for year in FinancialYear.objects.order_by('slug'):
        is_selected = year.slug == financial_year_id
        context['financial_years'].append({
            'id': year.slug,
            'is_selected': is_selected,
            'closest_match': {
                'is_exact_match': True,
                'slug': year.slug,
                'url_path': "/%s" % year.slug,
            },
        })

    response_yaml = yaml.safe_dump(context,
                                   default_flow_style=False,
                                   encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


class FinancialYearPage(View):
    slug = None
    organisational_unit = None

    def get(self, request, financial_year_id):
        context = {
            'selected_financial_year': financial_year_id,
            'financial_years': [],
            'slug': self.slug,
            'url_path': '/%s/%s' % (financial_year_id, self.slug),
            'organisational_unit': self.organisational_unit,
        }

        for year in FinancialYear.objects.order_by('slug'):
            is_selected = year.slug == financial_year_id
            context['financial_years'].append({
                'id': year.slug,
                'is_selected': is_selected,
                'closest_match': {
                    'is_exact_match': True,
                    'slug': self.slug,
                    'url_path': "/%s/%s" % (year.slug, self.slug),
                },
            })

        response_yaml = yaml.safe_dump(
            context,
            default_flow_style=False,
            encoding='utf-8'
        )
        return HttpResponse(response_yaml, content_type='text/x-yaml')


def department_list(request, financial_year_id):
    context = {
        'financial_years': [],
        'selected_financial_year': financial_year_id,
        'organisational_unit': 'department-list',
        'slug': 'departments',
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
                'organisational_unit': 'department-list',
                'url_path': "/%s/departments" % year.slug,
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
            sphere = selected_year \
                     .spheres \
                     .filter(slug=sphere_slug) \
                     .first()
            government = sphere \
                         .governments \
                         .filter(slug=government_slug) \
                         .first()
            department = government \
                         .departments \
                         .filter(slug=department_slug) \
                         .first()

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

    contributed_datasets = []
    for dataset in department.get_contributed_datasets():
        contributed_datasets.append({
            'name': dataset.name,
            'contributor': dataset.get_organization()['name'],
            'url_path': dataset.get_url_path(),
        })

    programme_budgets = department.get_programme_budgets()
    if not programme_budgets:
        programme_budgets = [
            {'name': p.name, 'total_budget': None}
            for p in department.programmes.order_by('programme_number')
        ]
    primary_department = department.get_primary_department()

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
            'slug': department.government.sphere.slug,
        },
        'selected_financial_year': financial_year_id,
        'financial_years': financial_years_context,
        'intro': department.intro,
        'treasury_datasets': department.get_treasury_resources(),
        'contributed_datasets': contributed_datasets if contributed_datasets else None,
        'programmes': programme_budgets,
        'government_functions': [f.name for f in department.get_govt_functions()],
        'organisational_unit': 'department',
        'is_vote_primary': department.is_vote_primary,
        'vote_primary': {
            'url_path': primary_department.get_url_path(),
            'name': primary_department.name,
            'slug': primary_department.slug
        }
    }

    response_yaml = yaml.safe_dump(context, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def contributed_dataset_list(request):
    context = {
        'datasets': [],
        'organisational_unit': 'dataset-list',
        'slug': 'contributed-data',
    }

    for dataset in Dataset.get_contributed_datasets():
        field_subset = dataset_fields(dataset)
        del field_subset['intro']
        del field_subset['methodology']
        context['datasets'].append(field_subset)

    response_yaml = yaml.safe_dump(context, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def dataset(request, dataset_slug):
    context = {
        'organisational_unit': 'dataset',
    }

    dataset = Dataset.fetch(dataset_slug)
    context.update(dataset_fields(dataset))

    response_yaml = yaml.safe_dump(context, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def dataset_fields(dataset):
    return {
        'slug': dataset.slug,
        'name': dataset.name,
        'resources': dataset.resources,
        'organization': dataset.get_organization(),
        'author': dataset.author,
        'created': dataset.created_date,
        'last_updated': dataset.last_updated_date,
        'license': dataset.license,
        'intro': dataset.intro,
        'methodology': dataset.methodology,
        'url_path': dataset.get_url_path(),
    }
