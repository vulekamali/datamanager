import urllib
from datetime import datetime

import urlparse

import requests
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views import View
from slugify import slugify

from budgetportal.csv_gen import generate_csv_response
from budgetportal.models import Video, Event, InfrastructureProjectPart
from budgetportal.openspending import PAGE_SIZE
from models import FinancialYear, Sphere, Department, InfrastructureProjectPart
from datasets import Dataset, Category
from summaries import (
    get_preview_page,
    get_focus_area_preview,
    get_consolidated_expenditure_treemap,
)
import yaml
import json
import logging
from . import revenue
from csv import DictWriter

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

logger = logging.getLogger(__name__)

COMMON_DESCRIPTION = "South Africa's National and Provincial budget data "
COMMON_DESCRIPTION_ENDING = "from National Treasury in partnership with IMALI YETHU."


def homepage_context(request, financial_year_id):
    """
    View of a financial year homepage, e.g. /2017-18
    """
    year = get_object_or_404(FinancialYear, slug=financial_year_id)
    revenue_data = year.get_budget_revenue()

    context = {
        'revenue': revenue.sort_categories(revenue_data),
        'selected_financial_year': financial_year_id,
        'selected_tab': 'homepage',
        'slug': financial_year_id,
        'title': "South African Government Budgets %s - vulekamali" % year.slug,
        'description': COMMON_DESCRIPTION + COMMON_DESCRIPTION_ENDING,
        'url_path': year.get_url_path(),
    }
    return context


def homepage_yaml(request, financial_year_id):
    context = homepage_context(request, financial_year_id)
    response_yaml = yaml.safe_dump(context,
                                   default_flow_style=False,
                                   encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def homepage(request):
    titles = {'whyBudgetIsImportant', 'howCanTheBudgetPortalHelpYou', 'theBudgetProcess'}
    videos = Video.objects.filter(title_id__in=titles)

    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    homepage_data_file_path = str(settings.ROOT_DIR.path('_data/index.yaml'))

    context = homepage_context(request, financial_year_id="2019-20")
    context['navbar'] = read_object_from_yaml(navbar_data_file_path)
    context['videos'] = videos
    context['latest_year'] = '2019-20'

    return render(request, 'homepage.html', context=context)


def search_result_page_context(request, financial_year_id):
    slug = 'search-result'
    context = {
        'financial_years': [],
        'selected_financial_year': financial_year_id,
        'selected_tab': None,
        'slug': slug,
        'title': "Search Results - vulekamali",
        'description': COMMON_DESCRIPTION + COMMON_DESCRIPTION_ENDING,
        'url_path': '/%s/%s' % (financial_year_id, slug),
    }

    for year in FinancialYear.get_available_years():
        is_selected = year.slug == financial_year_id
        context['financial_years'].append({
            'id': year.slug,
            'is_selected': is_selected,
            'closest_match': {
                'is_exact_match': True,
                'url_path': "/%s/%s" % (year.slug, slug),
            },
        })
    return context


def search_result_page_yaml(request, financial_year_id):
    context = search_result_page_context(request, financial_year_id)
    response_yaml = yaml.safe_dump(
        context,
        default_flow_style=False,
        encoding='utf-8'
    )
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def search_result(request, financial_year_id):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    context = search_result_page_context(request, financial_year_id)
    context['navbar'] = read_object_from_yaml(navbar_data_file_path)
    context['latest_year'] = '2019-20'
    return render(request, 'search-result.html', context=context)


def programme_list_csv(request, financial_year_id, sphere_slug):
    sphere = get_object_or_404(Sphere, financial_year__slug=financial_year_id, slug=sphere_slug)
    filename = "programmes-%s-%s.csv" % (financial_year_id, sphere_slug)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    fieldnames = [
        'government_name',
        'department_name',
        'programme_name',
        'programme_number',
    ]
    writer = DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    for government in sphere.governments.all():
        for department in government.departments.all():
            for programme in department.programmes.all():
                row = {
                    'government_name': government.name.encode("utf-8"),
                    'department_name': department.name.encode("utf-8"),
                    'programme_name': programme.name.encode("utf-8"),
                    'programme_number': programme.programme_number,
                }
                writer.writerow(row)
    return response


def department_list_for_sphere_csv(request, financial_year_id, sphere_slug):
    sphere = get_object_or_404(Sphere, financial_year__slug=financial_year_id, slug=sphere_slug)
    return department_list_csv(request, financial_year_id, [sphere_slug])


def department_list_csv(request, financial_year_id, spheres=['national', 'provincial']):
    selected_year = get_object_or_404(FinancialYear, slug=financial_year_id)

    filename = "departments-%s.csv" % (financial_year_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    fieldnames = [
        'government',
        'department_name',
        'vote_number',
        'is_vote_primary',
        'intro',
        'website_url',
    ]
    writer = DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    for sphere_name in spheres:
        for government in selected_year.spheres.filter(slug=sphere_name).first().governments.all():
            for department in government.departments.all():
                writer.writerow({
                    'government': government.name.encode("utf-8"),
                    'department_name': department.name.encode("utf-8"),
                    'vote_number': department.vote_number,
                    'is_vote_primary': department.is_vote_primary,
                    'intro': department.intro.encode("utf-8"),
                    'website_url': department.get_latest_website_url(),
                })

    return response


def department_list_data(financial_year_id):
    selected_year = get_object_or_404(FinancialYear, slug=financial_year_id)
    page_data = {
        'financial_years': [],
        'selected_financial_year': selected_year.slug,
        'selected_tab': 'departments',
        'slug': 'departments',
        'title': 'Department Budgets for %s - vulekamali' % selected_year.slug,
        'description': "Department budgets for the %s financial year %s" % (
            selected_year.slug, COMMON_DESCRIPTION_ENDING),
    }

    for year in FinancialYear.get_available_years():
        is_selected = year.slug == financial_year_id
        page_data['financial_years'].append({
            'id': year.slug,
            'is_selected': is_selected,
            'closest_match': {
                'is_exact_match': True,
                'url_path': "/%s/departments" % year.slug,
            },
        })

    for sphere_name in ('national', 'provincial'):
        page_data[sphere_name] = []
        for government in selected_year.spheres.filter(slug=sphere_name).first().governments.all():
            departments = []
            for department in government.departments.all():
                departments.append({
                    'name': department.name,
                    'slug': str(department.slug),
                    'vote_number': department.vote_number,
                    'url_path': department.get_url_path(),
                    'website_url': department.get_latest_website_url(),
                })
            departments = sorted(departments, key=lambda d: d['vote_number'])
            page_data[sphere_name].append({
                'name': government.name,
                'slug': str(government.slug),
                'departments': departments,
            })

    return page_data


def department_context(financial_year_id, sphere_slug, government_slug, department_slug):
    department = None
    selected_year = get_object_or_404(FinancialYear, slug=financial_year_id)

    years = FinancialYear.get_available_years()
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

    # ======== programmes =========================
    programmes = department.get_programme_budgets()
    if not programmes:
        programmes = {}
    if (not programmes) or (not programmes['programme_budgets']):
        programmes['programme_budgets'] = [
            {'name': p.name, 'total_budget': None}
            for p in department.programmes.order_by('programme_number')
        ]

    # ======= main budget docs =========================
    budget_dataset = department.get_dataset(
        group_name='budget-vote-documents')
    if budget_dataset:
        document_resource = budget_dataset.get_resource(format='PDF')
        if document_resource:
            document_resource = resource_fields(document_resource)
        tables_resource = (budget_dataset.get_resource(format='XLS') \
                           or budget_dataset.get_resource(format='XLSX'))
        if tables_resource:
            tables_resource = resource_fields(tables_resource)
        department_budget = {
            'name': budget_dataset.name,
            'document': document_resource,
            'tables': tables_resource,
        }
    else:
        department_budget = None

    # ======= adjusted budget docs =========================
    adjusted_budget_dataset = department.get_dataset(
        group_name='adjusted-budget-vote-documents')
    if adjusted_budget_dataset:
        document_resource = adjusted_budget_dataset.get_resource(format='PDF')
        if document_resource:
            document_resource = resource_fields(document_resource)
        tables_resource = (adjusted_budget_dataset.get_resource(format='XLS') \
                           or adjusted_budget_dataset.get_resource(format='XLSX'))
        if tables_resource:
            tables_resource = resource_fields(tables_resource)
        department_adjusted_budget = {
            'name': adjusted_budget_dataset.name,
            'document': document_resource,
            'tables': tables_resource,
        }
    else:
        department_adjusted_budget = None

    primary_department = department.get_primary_department()

    if department.government.sphere.slug == 'national':
        description_govt = "National"
    elif department.government.sphere.slug == 'provincial':
        description_govt = department.government.name

    context = {
        'economic_classification_by_programme': department.get_econ_by_programme_budgets(),
        'programme_by_economic_classification': department.get_prog_by_econ_budgets(),
        'subprogramme_by_programme': department.get_subprog_budgets(),
        'expenditure_over_time': department.get_expenditure_over_time(),
        'budget_actual': department.get_expenditure_time_series_summary(),
        'budget_actual_programmes': department.get_expenditure_time_series_by_programme(),
        'adjusted_budget_summary': department.get_adjusted_budget_summary(),
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
        'programmes': programmes,
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
        'department_budget': department_budget,
        'department_adjusted_budget': department_adjusted_budget,
        'vote_number': department.vote_number,
        'vote_primary': {
            'url_path': primary_department.get_url_path(),
            'name': primary_department.name,
            'slug': primary_department.slug
        },
        'website_url': department.get_latest_website_url(),
    }

    return context


def department_page(request, financial_year_id, sphere_slug, government_slug, department_slug):
    context = department_context(financial_year_id, sphere_slug, government_slug, department_slug)
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    context['navbar'] = read_object_from_yaml(navbar_data_file_path)
    context['latest_year'] = '2019-20'
    context['global_values'] = read_object_from_yaml(str(settings.ROOT_DIR.path('_data/global_values.yaml')))
    return render(request, 'department.html', context=context)


def department_yaml(request, financial_year_id, sphere_slug, government_slug, department_slug):
    context = department_context(financial_year_id, sphere_slug, government_slug, department_slug)
    response_yaml = yaml.safe_dump(context, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def dataset_category_list_data():
    page_data = {
        'categories': [category_fields(c) for c in Category.get_all()],
        'selected_tab': 'datasets',
        'slug': 'datasets',
        'name': 'Datasets and Analysis',
        'title': 'Datasets and Analysis - vulekamali',
        'url_path': '/datasets',
    }

    return page_data


def dataset_category_data(category_slug):
    category = Category.get_by_slug(category_slug)
    page_data = {
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
        page_data['datasets'].append(field_subset)

    return page_data


def dataset_data(category_slug, dataset_slug):
    dataset = Dataset.fetch(dataset_slug)
    assert (dataset.category.slug == category_slug)

    if category_slug == 'contributed':
        description = ("Data and/or documentation related to South African"
                       " government budgets contributed by %s and hosted"
                       " by National Treasury in partnership with IMALI YETHU"
                       ) % dataset.get_organization()['name']
    else:
        description = dataset.intro

    page_data = {
        'selected_tab': 'datasets',
        'title': "%s - vulekamali" % dataset.name,
        'description': description,
    }

    page_data.update(dataset_fields(dataset))
    return page_data


def infrastructure_projects_overview(request):
    """ Overview page to showcase all featured infrastructure projects """
    infrastructure_projects = InfrastructureProjectPart.objects.filter(featured=True).distinct('project_slug')
    if infrastructure_projects is None:
        raise Http404()
    projects = []
    for project in infrastructure_projects:
        departments = Department.objects.filter(
            slug=slugify(project.department),
            government__sphere__slug='national'
        )
        department_url = None
        if departments:
            department_url = departments[0].get_latest_department_instance().get_url_path()
        projects.append({
            'name': project.project_name,
            'coordinates': project.clean_coordinates(project.gps_code),
            'projected_budget': project.calculate_projected_expenditure(),
            'stage': project.current_project_stage,
            'description': project.project_description,
            'provinces': project.provinces.split(','),
            'total_budget': project.total_project_cost,
            'detail': project.get_url_path(),
            'slug': project.get_url_path(),
            'page_title': '{} - vulekamali'.format(project.project_name),
            'department': {
                'name': project.department,
                'url': department_url,
            },
            'nature_of_investment': project.nature_of_investment,
            'infrastructure_type': project.infrastructure_type,
            'expenditure': sorted(project.build_complete_expenditure(), key=lambda e: e['year'])
        })
    projects = sorted(projects, key=lambda p: p['name'])
    return {
        'dataset_url': InfrastructureProjectPart.get_dataset().get_url_path(),
        'projects': projects,
        'description': 'Infrastructure projects in South Africa for 2019-20',
        'slug': 'infrastructure-projects',
        'selected_tab': 'infrastructure-projects',
        'title': 'Infrastructure Projects - vulekamali',
    }


def infrastructure_projects_overview_yaml(request):
    response = infrastructure_projects_overview(request)
    response_yaml = yaml.safe_dump(response, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def infrastructure_projects_overview_json(request):
    response_json = json.dumps(
        infrastructure_projects_overview(request),
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )
    return HttpResponse(response_json, content_type="application/json")


def infrastructure_project_list(request):
    context = {
        "page": {"layout": "about", "data_key": "about"},
        "site": {"latest_year": "2019-20"},
    }
    return render(request, "infrastructure_project_list.html", context=context)


def infrastructure_project_detail_data(project_slug):
    project = InfrastructureProjectPart.objects.filter(project_slug=project_slug).first()
    if not project:
        return HttpResponse(status=404)
    dataset = project.get_dataset()
    if not dataset:
        return HttpResponse(status=404)

    departments = Department.objects.filter(
        slug=slugify(project.department),
        government__sphere__slug='national'
    )
    department_url = None
    if departments:
        department_url = departments[0].get_latest_department_instance().get_url_path()

    project = {
        'name': project.project_name,
        'coordinates': project.clean_coordinates(project.gps_code),
        'projected_budget': project.calculate_projected_expenditure(),
        'stage': project.current_project_stage,
        'description': project.project_description,
        'provinces': project.provinces.split(','),
        'total_budget': project.total_project_cost,
        'detail': project.get_url_path(),
        'dataset_url': dataset.get_url_path(),
        'slug': project.get_url_path(),
        'page_title': '{} - vulekamali'.format(project.project_name),
        'department': {
            'name': project.department,
            'url': department_url,
            'budget_document': project.get_budget_document_url()
        },
        'nature_of_investment': project.nature_of_investment,
        'infrastructure_type': project.infrastructure_type,
        'expenditure': sorted(project.build_complete_expenditure(), key=lambda e: e['year'])
    }
    return {
        'dataset_url': InfrastructureProjectPart.get_dataset().get_url_path(),
        'projects': [project],
        'description': 'Infrastructure projects in South Africa for 2019-20',
        'slug': 'infrastructure-projects',
        'selected_tab': 'infrastructure-projects',
        'title': 'Infrastructure Projects - vulekamali',
    }


def infrastructure_project_detail_yaml(request, project_slug):
    response = infrastructure_project_detail_data(project_slug)
    if isinstance(response, HttpResponse):
        return response

    response_yaml = yaml.safe_dump(response, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def infrastructure_project_detail_json(request, project_slug):
    response = infrastructure_project_detail_data(project_slug)
    if isinstance(response, HttpResponse):
        return response

    response_json = json.dumps(
        response,
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )
    return HttpResponse(response_json, content_type="application/json")


def infrastructure_project_detail(request, project_slug):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    context = {
        'page': {
            'layout': 'infrastructure_project',
            'data_key': 'dataset',
        },
        'site': {
            'data': {
                'navbar': read_object_from_yaml(navbar_data_file_path),
                'dataset': infrastructure_project_detail_data(project_slug),
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'infrastructure_project.html', context=context)


def openspending_csv(request):
    """
    Ensure that API call is to OpenSpending *
    Get result from API call
    Feed dict result to CSV generator
    Return streaming http response
    :param request: HttpRequest
    :return: StreamingHttpResponse
    """
    api_url = urllib.unquote(str(request.GET.get('api_url')))

    parsed_url = urlparse.urlparse(api_url)
    domain = '{uri.netloc}'.format(uri=parsed_url)
    if domain != 'openspending.org':
        return HttpResponse("Invalid domain received: %s (Only openspending.org is allowed)" % domain,
                            status=403)

    result = requests.get(api_url)
    logger.info(
        "request %s took %dms",
        api_url,
        result.elapsed.microseconds / 1000
    )
    result.raise_for_status()
    if result.json()['total_cell_count'] > PAGE_SIZE:
        raise Exception("More cells than expected - perhaps we should start paging")
    return generate_csv_response(result.json())


def dataset_fields(dataset):
    return {
        'slug': dataset.slug,
        'name': dataset.name,
        'resources': [resource_fields(r) for r in dataset.resources],
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


def resource_fields(resource):
    return {
        'name': resource['name'],
        'url': resource['url'],
        'description': resource['description'],
        'format': resource['format'],
    }


def category_fields(category):
    return {
        'name': category.name,
        'slug': category.slug,
        'url_path': category.get_url_path(),
        'description': category.description,
    }


def about(request):
    videos_data = Video.objects.filter(title_id='onlineBudgetPortal')
    about_date_file_path = str(settings.ROOT_DIR.path('_data/about.yaml'))
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    context = {
        'page': {
            'layout': 'about',
            'data_key': 'about'
        },
        'site': {
            'data': {
                'videos': {'data': videos_data},
                'about': read_object_from_yaml(about_date_file_path),
                'navbar': read_object_from_yaml(navbar_data_file_path)
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'about.html', context=context)


def static_search_data(request):
    glossary_data_file_path = str(settings.ROOT_DIR.path('_data/glossary.json'))
    with open(glossary_data_file_path) as glossary_file:
        glossary_data = json.load(glossary_file)
    context = {
        "videos": [model_to_dict(v) for v in Video.objects.all()],
        "glossary": glossary_data,
    }

    response_json = json.dumps(
        context,
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
        cls=DjangoJSONEncoder
    )
    return HttpResponse(response_json, content_type="application/json")


def events(request):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))

    upcoming_events = Event.objects.filter(status='upcoming')
    past_events = Event.objects.filter(status='past')

    context = {
        'page': {
            'layout': 'events',
            'data_key': 'events'
        },
        'site': {
            'data': {
                'events': {
                    'upcoming': upcoming_events,
                    'past': past_events
                },
                'navbar': read_object_from_yaml(navbar_data_file_path),
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'events.html', context=context)


def glossary(request):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    context = {
        'page': {
            'layout': 'glossary',
            'data_key': 'glossary'
        },
        'site': {
            'data': {
                'navbar': read_object_from_yaml(navbar_data_file_path),
                'glossary': {
                    'selected_tab': 'learning-centre',
                    'selected_sidebar': 'glossary',
                    'title': 'Glossary - vulekamali',
                    'description': "South Africa's National and Provincial budget data from National Treasury in partnership with IMALI YETHU.",
                }
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'glossary.html', context=context)


def faq(request):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    context = {
        'page': {
            'layout': 'faq',
            'data_key': 'faq'
        },
        'site': {
            'data': {
                'navbar': read_object_from_yaml(navbar_data_file_path),
                'faq': {
                    'title': 'FAQ - vulekamali',
                    'description': "South Africa's National and Provincial budget data from National Treasury in partnership with IMALI YETHU.",
                    'selected_tab': 'faq'
                },
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'faq.html', context=context)


def videos(request):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))

    videos_data = Video.objects.all()

    context = {
        'page': {
            'layout': 'videos',
            'data_key': 'videos'
        },
        'site': {
            'data': {
                'videos': {
                    'title': 'Videos - vulekamali',
                    'description': "South Africa's National and Provincial budget data from National Treasury in partnership with IMALI YETHU.",
                    'selected_tab': 'learning-centre',
                    'selected_sidebar': 'videos',
                    'data': videos_data
                },
                'navbar': read_object_from_yaml(navbar_data_file_path)
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'videos.html', context=context)


def terms_and_conditions(request):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    context = {
        'page': {
            'layout': 'terms-and-conditions',
            'data_key': 'terms-and-conditions'
        },
        'site': {
            'data': {
                'navbar': read_object_from_yaml(navbar_data_file_path)
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'terms-and-conditions.html', context=context)


def resources(request):
    resources_file_path = str(settings.ROOT_DIR.path('_data/resources.yaml'))
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))

    titles = {'theBudgetProcess', 'participate'}
    videos_data = Video.objects.filter(title_id__in=titles)

    context = {
        'page': {
            'layout': 'resources',
            'data_key': 'resources',
        },
        'site': {
            'data': {
                'navbar': read_object_from_yaml(navbar_data_file_path),
                'videos': {'data': videos_data},
                'resources': read_object_from_yaml(resources_file_path),
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'resources.html', context=context)


def guides(request, slug):
    if slug not in [
        'index',
        'adjusted-estimates-of-national-expenditure',
        'estimates-of-national-expenditure',
        'estimates-of-provincial-expenditure',
        'performance-and-expenditure-reviews',
        'frameworks-for-conditional-grants'
    ]: return HttpResponse(status=404)
    aene_file_path = str(settings.ROOT_DIR.path('_data/guides/adjusted-estimates-of-national-expenditure.yaml'))
    ene_file_path = str(settings.ROOT_DIR.path('_data/guides/estimates-of-national-expenditure.yaml'))
    epre_file_path = str(settings.ROOT_DIR.path('_data/guides/estimates-of-provincial-expenditure.yaml'))
    per_file_path = str(settings.ROOT_DIR.path('_data/guides/performance-and-expenditure-reviews.yaml'))
    index_file_path = str(settings.ROOT_DIR.path('_data/guides/index.yaml'))
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    context = {
        'page': {
            'layout': 'guides',
            'data_key': slug,
            'content_template': 'guide-{}.html'.format(slug)
        },
        'site': {
            'data': {
                'navbar': read_object_from_yaml(navbar_data_file_path),
                'guides': {
                    'index': read_object_from_yaml(index_file_path),
                    'adjusted-estimates-of-national-expenditure': read_object_from_yaml(aene_file_path),
                    'estimates-of-national-expenditure': read_object_from_yaml(ene_file_path),
                    'estimates-of-provincial-expenditure': read_object_from_yaml(epre_file_path),
                    'performance-and-expenditure-reviews': read_object_from_yaml(per_file_path),
                }
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    if slug == 'index':
        template = 'guides'
    else:
        template = 'guide_item'
    return render(request, '{}.html'.format(template), context=context)


def dataset_landing_page_yaml(request):
    response = dataset_category_list_data()
    response_yaml = yaml.safe_dump(response, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def dataset_landing_page(request):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    context = {
        'page': {
            'layout': 'dataset_landing_page',
            'data_key': 'datasets',
        },
        'site': {
            'data': {
                'navbar': read_object_from_yaml(navbar_data_file_path),
                'datasets': {
                    'index': dataset_category_list_data()
                }
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'datasets.html', context=context)


def dataset_category_yaml(request, category_slug):
    response = dataset_category_data(category_slug)
    response_yaml = yaml.safe_dump(response, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def dataset_category_migrated(request, category_slug):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    context = {
        'page': {
            'layout': 'government_dataset_category',
            'data_key': category_slug,
        },
        'site': {
            'data': {
                'navbar': read_object_from_yaml(navbar_data_file_path),
                'dataset': dataset_category_data(category_slug),
                'guide': {'slug': category_slug, 'url': 'guides/{}'.format(category_slug)}
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'government_dataset_category.html', context=context)


def dataset_yaml(request, category_slug, dataset_slug):
    response = dataset_data(category_slug, dataset_slug)
    response_yaml = yaml.safe_dump(response, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def dataset_migrated(request, category_slug, dataset_slug):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    context = {
        'page': {
            'layout': 'government_dataset',
            'data_key': dataset_slug,
            'category': category_slug,
        },
        'site': {
            'data': {
                'navbar': read_object_from_yaml(navbar_data_file_path),
                'dataset': dataset_data(category_slug, dataset_slug)
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'government_dataset.html', context=context)


def contributed_datasets_list(request):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    context = {
        'page': {
            'layout': 'contributed-data',
            'data_key': 'contributed',
        },
        'site': {
            'data': {
                'navbar': read_object_from_yaml(navbar_data_file_path),
                'dataset': dataset_category_data('contributed'),
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'contributed-data.html', context=context)


def contributed_dataset(request, dataset_slug):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    dataset = dataset_data('contributed', dataset_slug)
    dataset["created"] = datetime.strptime(dataset["created"], "%Y-%m-%dT%H:%M:%S.%f")
    dataset["last_updated"] = datetime.strptime(dataset["last_updated"], "%Y-%m-%dT%H:%M:%S.%f")
    context = {
        'page': {
            'layout': 'contributed_dataset',
            'data_key': 'contributed',
            'category': 'contributed',
        },
        'site': {
            'data': {
                'navbar': read_object_from_yaml(navbar_data_file_path),
                'dataset': dataset,
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'contributed_dataset.html', context=context)


def read_object_from_yaml(path_file):
    with open(path_file, 'r') as f:
        return yaml.load(f)


def department_list(request, financial_year_id):
    context = department_list_data(financial_year_id)
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))
    context['navbar'] = read_object_from_yaml(navbar_data_file_path)
    context['latest_year'] = '2019-20'
    return render(request, 'department_list.html', context=context)


def department_list_yaml(request, financial_year_id):
    page_data = department_list_data(financial_year_id)
    response_yaml = yaml.safe_dump(page_data, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def department_list_json(request, financial_year_id):
    response_json = json.dumps(
        department_list_data(financial_year_id),
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
        cls=DjangoJSONEncoder
    )
    return HttpResponse(response_json, content_type="application/json")


def treemaps_data(financial_year_id, phase_slug, sphere_slug):
    """ The data for the vulekamali home page treemaps """
    dept = Department.objects.filter(government__sphere__slug=sphere_slug)[0]
    if sphere_slug == 'national':
        page_data = dept.get_national_expenditure_treemap(financial_year_id, phase_slug)
    elif sphere_slug == 'provincial':
        page_data = dept.get_provincial_expenditure_treemap(financial_year_id, phase_slug)
    else:
        return HttpResponse("Unknown government sphere.", status=400)
    return page_data


def treemaps_yaml(request, financial_year_id, phase_slug, sphere_slug):
    response = treemaps_data(financial_year_id, phase_slug, sphere_slug)
    response_yaml = yaml.safe_dump(response, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def treemaps_json(request, financial_year_id, phase_slug, sphere_slug):
    response_json = json.dumps(
        treemaps_data(financial_year_id, phase_slug, sphere_slug),
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )
    return HttpResponse(response_json, content_type="application/json")


def consolidated_treemap(financial_year_id):
    """ The data for the vulekamali home page treemaps """
    financial_year = FinancialYear.objects.get(slug=financial_year_id)
    page_data = get_consolidated_expenditure_treemap(financial_year)
    return page_data


def consolidated_treemap_yaml(request, financial_year_id):
    response = consolidated_treemap(financial_year_id)
    response_yaml = yaml.safe_dump(response, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def consolidated_treemap_json(request, financial_year_id):
    response_json = json.dumps(
        consolidated_treemap(financial_year_id),
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )
    return HttpResponse(response_json, content_type="application/json")


def focus_preview_data(financial_year_id):
    """ The data for the focus area preview pages for a specific year """
    financial_year = FinancialYear.objects.get(slug=financial_year_id)
    page_data = get_focus_area_preview(financial_year)
    return page_data


def focus_preview_yaml(request, financial_year_id):
    response = focus_preview_data(financial_year_id)
    response_yaml = yaml.safe_dump(response, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def focus_preview_json(request, financial_year_id):
    response_json = json.dumps(
        focus_preview_data(financial_year_id),
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )
    return HttpResponse(response_json, content_type="application/json")


def focus_area_preview(request, financial_year_id, focus_slug):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))

    context = {
        'page': {
            'layout': 'focus_page',
            'data_key': '',
        },
        'site': {
            'data': {
                'navbar': read_object_from_yaml(navbar_data_file_path),
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'focus_page.html', context=context)


def department_preview_data(financial_year_id, sphere_slug, government_slug, phase_slug):
    page_data = get_preview_page(financial_year_id, phase_slug, government_slug, sphere_slug)
    return page_data


def department_preview_yaml(request, financial_year_id, sphere_slug, government_slug, phase_slug):
    response = department_preview_data(financial_year_id, sphere_slug, government_slug, phase_slug)
    response_yaml = yaml.safe_dump(response, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml, content_type='text/x-yaml')


def department_preview_json(request, financial_year_id, sphere_slug, government_slug, phase_slug):
    response_json = json.dumps(
        department_preview_data(financial_year_id, sphere_slug, government_slug, phase_slug),
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )
    return HttpResponse(response_json, content_type="application/json")


def department_preview(request, financial_year_id, sphere_slug, government_slug, department_slug):
    navbar_data_file_path = str(settings.ROOT_DIR.path('_data/navbar.yaml'))

    context = {
        'page': {
            'layout': 'department_preview',
            'data_key': '',
        },
        'site': {
            'data': {
                'navbar': read_object_from_yaml(navbar_data_file_path),
            },
            'latest_year': '2019-20'
        },
        'debug': settings.DEBUG
    }
    return render(request, 'department_preview.html', context=context)
