from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from models import FinancialYear, Dataset, Category
import yaml

from . import revenue

COMMON_DESCRIPTION = "South Africa's National and Provincial budget data "
COMMON_DESCRIPTION_ENDING = "from National Treasury in partnership with IMALI YETHU."


def year_home(request, financial_year_id):
    """
    View of a financial year homepage, e.g. /2017-18
    """
    year = get_object_or_404(FinancialYear, slug=financial_year_id)
    revenue_data = year.get_budget_revenue()

    context = {
        'financial_years': [],
        'revenue': revenue.sort_categories(revenue_data),
        'selected_financial_year': financial_year_id,
        'selected_tab': 'homepage',
        'slug': financial_year_id,
        'title': "South African Government Budgets %s - vulekamali" % year.slug,
        'description': COMMON_DESCRIPTION + COMMON_DESCRIPTION_ENDING,
        'url_path': year.get_url_path(),
    }
    for year in FinancialYear.objects.order_by('slug'):
        is_selected = year.slug == financial_year_id
        context['financial_years'].append({
            'id': year.slug,
            'is_selected': is_selected,
            'closest_match': {
                'is_exact_match': True,
                'url_path': "/%s" % year.slug,
            },
        })

    response_yaml = yaml.safe_dump(context,
                                   default_flow_style=False,
                                   encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


class FinancialYearPage(View):
    """
    Generic page data for pages specific to a financial year
    """
    slug = None
    selected_tab = None

    def get(self, request, financial_year_id):
        context = {
            'financial_years': [],
            'selected_financial_year': financial_year_id,
            'selected_tab': self.selected_tab,
            'slug': self.slug,
            'title': "Search Result - vulekamali",
            'description': COMMON_DESCRIPTION + COMMON_DESCRIPTION_ENDING,
            'url_path': '/%s/%s' % (financial_year_id, self.slug),
        }

        for year in FinancialYear.objects.order_by('slug'):
            is_selected = year.slug == financial_year_id
            context['financial_years'].append({
                'id': year.slug,
                'is_selected': is_selected,
                'closest_match': {
                    'is_exact_match': True,
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
    selected_year = get_object_or_404(FinancialYear, slug=financial_year_id)
    context = {
        'financial_years': [],
        'selected_financial_year': selected_year.slug,
        'selected_tab': 'departments',
        'slug': 'departments',
        'title': 'Department Budgets for %s - vulekamali' % selected_year.slug,
        'description': "Department budgets for the %s financial year %s" % (
         selected_year.slug, COMMON_DESCRIPTION_ENDING),
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
    selected_year = get_object_or_404(FinancialYear, slug=financial_year_id)

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
                'url_path': closest_match.get_url_path(),
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

    if department.government.sphere.slug == 'national':
        description_govt = "National"
    elif department.government.sphere.slug == 'provincial':
        description_govt = department.government.name

    context = {
        'expenditure_over_time': department.get_expenditure_over_time(),
        'contributed_datasets': contributed_datasets if contributed_datasets else None,
        'financial_years': financial_years_context,
        'government': {
            'name': department.government.name,
            'slug': str(department.government.slug),
        },
        'government_functions': [f.name for f in department.get_govt_functions()],
        'intro': department.intro,
        'is_vote_primary': department.is_vote_primary,
        'name': department.name,
        'slug': str(department.slug),
        'sphere': {
            'name': department.government.sphere.name,
            'slug': department.government.sphere.slug,
        },
        'programmes': programme_budgets,
        'selected_financial_year': financial_year_id,
        'selected_tab': 'departments',
        'title': "%s budget %s  - vulekamali" % (
            department.name, selected_year.slug),
        'description': "%s department: %s budget data for the %s financial year %s" % (
            description_govt,
            department.name,
            selected_year.slug,
            COMMON_DESCRIPTION_ENDING,
        ),
        'treasury_datasets': department.get_treasury_resources(),
        'vote_number': department.vote_number,
        'vote_primary': {
            'url_path': primary_department.get_url_path(),
            'name': primary_department.name,
            'slug': primary_department.slug
        },
    }

    response_yaml = yaml.safe_dump(context, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def dataset_category(request, category_slug):
    category = Category.get_by_slug(category_slug)
    context = {
        'datasets': [],
        'selected_tab': 'datasets',
        'slug': category.slug,
        'name': category.name,
        'title': '%s - vulekamali' % category.name,
        'description': category.description,
        'url_path': category.get_url_path(),
    }

    for dataset in category.get_datasets():
        field_subset = dataset_fields(dataset)
        field_subset['description'] = field_subset.pop('intro')
        del field_subset['methodology']
        del field_subset['key_points']
        del field_subset['use_for']
        del field_subset['usage']
        context['datasets'].append(field_subset)

    response_yaml = yaml.safe_dump(context, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def dataset(request, category_slug, dataset_slug):
    dataset = Dataset.fetch(dataset_slug)
    assert(dataset.category.slug == category_slug)

    if category_slug == 'contributed':
        description = ("Data and/or documentation related to South African"
                       " government budgets contributed by %s and hosted"
                       " by National Treasury in partnership with IMALI YETHU"
        ) % dataset.get_organization()['name']
    else:
        description = dataset.intro

    context = {
        'selected_tab': 'datasets',
        'title': "%s - vulekamali" % dataset.name,
        'description': description,
    }

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
        'intro_short': dataset.intro_short,
        'key_points': dataset.key_points,
        'use_for': dataset.use_for,
        'usage': dataset.usage,
        'methodology': dataset.methodology,
        'url_path': dataset.get_url_path(),
        'category': category_fields(dataset.category),
    }


def category_fields(category):
    return {
        'name': category.name,
        'slug': category.slug,
        'url_path': category.get_url_path(),
        'description': category.description,
    }
