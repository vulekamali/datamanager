from django.http import HttpResponse, Http404
from ckanapi import RemoteCKAN
import yaml
ckan = RemoteCKAN('https://treasurydata.openup.org.za')


def department(request, financial_year, sphere, geographic_region_slug, department_name_slug):
        raise Exception("Department not found")
    department_package = response['results'][0]
    financial_years_context = []
    # for year in financial_years:
    #     closest_match, closest_is_exact = year.get_closest_match(department)
    #     financial_years_context.append({
    #         'id': year.id,
    #         'is_selected': year == department.government.sphere.financial_year,
    #         'closest_match': {
    #             'name': closest_match.name,
    #             'slug': closest_match.slug,
    #             'url_path': closest_match.get_url_path(),
    #             'organisational_unit': closest_match.organisational_unit,
    #             'is_exact_match': closest_is_exact,
    #         },
    #     })
    # financial_years_context = sorted(financial_years_context, key=lambda y: y['id'])
    context = {
        'name': department_package['name'],
    #     'slug': department.slug,
    #     'vote_number': department.vote_number,
    #     'government': {
    #         'name': department.government.name,
    #         'slug': department.government.slug,
    #     },
    #     'financial_years': financial_years_context,
    #     'narrative': department.narrative,
    }

    response_yaml = yaml.safe_dump(context, default_flow_style=False, encoding='utf-8')
    return HttpResponse(response_yaml)
