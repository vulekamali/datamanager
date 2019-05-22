from slugify import slugify
from models import (
    Department,
    FinancialYear,
    EXPENDITURE_TIME_SERIES_PHASE_MAPPING,
)
import logging
from datasets import (
    get_expenditure_time_series_dataset,
    get_consolidated_expenditure_budget_dataset,
)

logger = logging.getLogger(__name__)


PROV_EQ_SHARE_DEPT = 'National Treasury'
PROV_EQ_SHARE_SUBPROG = 'Provincial Equitable Share'


def get_focus_area_preview(financial_year):
    """ Returns data for the focus area preview pages. """

    national_expenditure_results, national_os_api = get_focus_area_data(
        financial_year, 'national')
    provincial_expenditure_results, provincial_os_api = get_focus_area_data(
        financial_year, 'provincial')
    subprogramme_to_exclude_results = get_subprogramme_from_actual_and_budgeted_dataset(
        'national', PROV_EQ_SHARE_DEPT, PROV_EQ_SHARE_SUBPROG
    )
    nat_function_ref = national_os_api.get_function_ref()
    prov_function_ref = provincial_os_api.get_function_ref()

    function_names = [cell[nat_function_ref]
                      for cell in national_expenditure_results['cells']]
    function_names += [cell[prov_function_ref]
                       for cell in provincial_expenditure_results['cells']]
    unique_functions = list(set(function_names))

    function_objects = []
    for function in unique_functions:
        function_objects.append({
            'title': function,
            'slug': slugify(function),
            'national': national_summary_for_function(
                function,
                national_os_api,
                national_expenditure_results,
                subprogramme_to_exclude_results,
            ),
            'provincial': provincial_summary_for_function(
                function,
                provincial_os_api,
                provincial_expenditure_results,
            ),
        })

    return {
        'data': {
            'items': function_objects,
        },
    } if function_objects else None


def get_focus_area_data(financial_year, sphere_slug):
    dataset = get_expenditure_time_series_dataset(sphere_slug)
    if not dataset:
        return None, None
    openspending_api = dataset.get_openspending_api()
    year_ref = openspending_api.get_financial_year_ref()
    dept_ref = openspending_api.get_department_name_ref()
    function_ref = openspending_api.get_function_ref()
    phase_ref = openspending_api.get_phase_ref()
    government_ref = openspending_api.get_geo_ref()

    cuts = [
        year_ref + ':' + '{}'.format(financial_year.get_starting_year()),
        phase_ref + ':' + '{}'.format("Main appropriation"),
    ]

    drilldowns = [
        function_ref,
        dept_ref
    ]

    if sphere_slug == 'provincial':
        drilldowns.append(government_ref)

    results = openspending_api.aggregate(cuts=cuts, drilldowns=drilldowns)
    cells = results['cells']
    cells = filter(lambda c: c[function_ref] != '', cells)

    return cells, openspending_api


def get_subprogramme_from_actual_and_budgeted_dataset(financial_year, sphere_slug, department, subprogramme):
    dataset = get_expenditure_time_series_dataset(sphere_slug)
    if not dataset:
        return None, None
    openspending_api = dataset.get_openspending_api()
    year_ref = openspending_api.get_financial_year_ref()
    dept_ref = openspending_api.get_department_name_ref()
    function_ref = openspending_api.get_function_ref()
    phase_ref = openspending_api.get_phase_ref()
    subprogramme_ref = openspending_api.get_subprogramme_name_ref()

    expenditure_cuts = [
        year_ref + ':' + '{}'.format(financial_year.get_starting_year()),
        phase_ref + ':' + '{}'.format("Main appropriation"),
        dept_ref + ':' + '{}'.format(department),
        subprogramme_ref + ':' + '{}'.format(subprogramme),
    ]

    expenditure_drilldowns = [
        function_ref
    ]

    expenditure_results = openspending_api.aggregate(
        cuts=expenditure_cuts, drilldowns=expenditure_drilldowns)
    return expenditure_results


def national_summary_for_function(
        financial_year,
        function,
        openspending_api,
        expenditure_results,
        subprogramme_to_exclude_results):
    dept_ref = openspending_api.get_department_name_ref()
    function_ref = openspending_api.get_function_ref()

    function_cells = filter(lambda x: x[function_ref] == function,
                            expenditure_results['cells'])
    national = {'data': [], 'footnotes': [], 'notices': []}
    national['total'] = sum(c['value.sum'] for c in function_cells)

    if not function_cells:
        notice = ("No national departments allocated budget to this focus area.")
        national['notices'].append(notice)
    national['footnotes'].append(
        '**Source:** Estimates of National Expenditure {}'.format(financial_year.slug))
    for cell in function_cells:
        exclude_for_function = filter(lambda x: x[function_ref] == function,
                                      subprogramme_to_exclude_results['cells'])
        if exclude_for_function and cell[dept_ref] == PROV_EQ_SHARE_DEPT:
            exclude_amount = exclude_for_function[0]['value.sum']
            amount = cell['value.sum'] - exclude_amount
            national['footnotes'].append(
                '**Note:** Provincial Equitable Share is excluded')
        else:
            amount = cell['value.sum']
        department_slug = slugify(cell[dept_ref])
        try:
            department = Department.objects.get(
                slug=department_slug,
                government__sphere__slug='national',
                government__sphere__financial_year=financial_year,
            )
            preview_url = department.get_preview_url_path()
        except Department.DoesNotExist:
            preview_url = None
        national['data'].append({
            'title': cell[dept_ref],
            'slug': department_slug,
            'amount': amount,
            'url': preview_url,
        })
    return national


def provincial_summary_for_function(financial_year, function, openspending_api, expenditure_results):
    dept_ref = openspending_api.get_department_name_ref()
    function_ref = openspending_api.get_function_ref()
    geo_ref = openspending_api.get_geo_ref()
    no_provincial_in_year = not expenditure_results['cells']

    function_cells = filter(lambda x: x[function_ref] == function,
                            expenditure_results['cells'])
    provincial = {'data': [], 'footnotes': [], 'notices': []}
    if no_provincial_in_year:
        provincial['total'] = None
    else:
        provincial['total'] = sum(c['value.sum'] for c in function_cells)

    if no_provincial_in_year:
        notice = ("Provincial budget allocations to focus areas "
                  "for {} not published yet on vulekamali.").format(financial_year.slug)
        provincial['notices'].append(notice)
    else:
        footnote = '**Source:** Estimates of Provincial Expenditure {}'.format(
            financial_year.slug)
        provincial['footnotes'].append(footnote)

        if not function_cells:
            notice = (
                "No provincial departments allocated budget to this focus area.")
            provincial['notices'].append(notice)

        for cell in function_cells:
            department_slug = slugify(cell[dept_ref])
            try:
                department = Department.objects.get(
                    slug=department_slug,
                    government__name=cell[geo_ref],
                    government__sphere__slug='provincial',
                    government__sphere__financial_year=financial_year,
                )
                preview_url = department.get_preview_url_path()
            except Department.DoesNotExist:
                preview_url = None
            provincial['data'].append({
                'name': cell[dept_ref],
                'slug': department_slug,
                'amount': cell['value.sum'],
                'url': preview_url,
                'province': cell[geo_ref],
            })
    return provincial


def get_focus_area_url_path(financial_year_slug, name):
    if name == "Contingency reserve":
        return None
    return "{}/focus/{}".format(financial_year_slug, slugify(name))


def get_consolidated_expenditure_treemap(financial_year):
    """ Returns a data object for each function group for a specific year. Used by the consolidated treemap. """

    expenditure = []
    dataset = get_consolidated_expenditure_budget_dataset()
    if not dataset:
        return None
    openspending_api = dataset.get_openspending_api()
    year_ref = openspending_api.get_financial_year_ref()

    # Add cuts: year and phase
    expenditure_cuts = [
        year_ref + ':' + '{}'.format(financial_year.get_starting_year()),
    ]
    expenditure_drilldowns = [
        openspending_api.get_function_ref(),
    ]

    expenditure_results = openspending_api.aggregate(
        cuts=expenditure_cuts, drilldowns=expenditure_drilldowns)

    total_budget = 0
    modified_result_cells = []

    for cell in expenditure_results['cells']:
        total_budget += float(cell['value.sum'])
        modified_result_cells.append(cell)

    for cell in modified_result_cells:
        percentage_of_total = float(cell['value.sum']) / total_budget * 100
        focus_area_name = cell[openspending_api.get_function_ref()]
        expenditure.append({
            'name': focus_area_name,
            'id': slugify(cell[openspending_api.get_function_ref()]),
            'amount': float(cell['value.sum']),
            'percentage': percentage_of_total,
            'url': get_focus_area_url_path(focus_area_name)
        })

    return {
        'data': {
            'items': expenditure,
            'total': total_budget
        },
    } if expenditure else None


def get_preview_page(financial_year_id, phase_slug, government_slug, sphere_slug):
    try:
        selected_phase = EXPENDITURE_TIME_SERIES_PHASE_MAPPING[phase_slug]
    except KeyError:
        raise Exception('An invalid phase was provided: {}'.format(phase_slug))

    expenditure = []
    dataset = get_expenditure_time_series_dataset(sphere_slug)
    if not dataset:
        return None
    openspending_api = dataset.get_openspending_api()
    programme_ref = openspending_api.get_programme_name_ref()
    geo_ref = openspending_api.get_geo_ref()
    department_ref = openspending_api.get_department_name_ref()
    financial_year = FinancialYear.objects.get(slug=financial_year_id)
    function_ref = openspending_api.get_function_ref()

    # Expenditure data
    expenditure_cuts = [
        openspending_api.get_adjustment_kind_ref() + ':' + '"Total"',
        openspending_api.get_financial_year_ref() + ':' + '{}'.format(
            FinancialYear.start_from_year_slug(financial_year_id)
        ),
        openspending_api.get_phase_ref() + ':' + '"{}"'.format(selected_phase)
    ]
    expenditure_drilldowns = [
        department_ref,
        geo_ref,
        programme_ref,
        function_ref
    ]
    expenditure_results = openspending_api.aggregate(
        cuts=expenditure_cuts, drilldowns=expenditure_drilldowns)

    # We do a separate call to always build focus area data from the main
    # appropriation phase
    focus_cuts = [
        openspending_api.get_adjustment_kind_ref() + ':' + '"Total"',
        openspending_api.get_financial_year_ref() + ':' + '{}'.format(
            FinancialYear.start_from_year_slug(financial_year_id)
        ),
        openspending_api.get_phase_ref() + ':' +
        '"{}"'.format(EXPENDITURE_TIME_SERIES_PHASE_MAPPING["original"]),
    ]
    focus_drilldowns = [
        department_ref,
        geo_ref,
        function_ref
    ]

    focus_results = openspending_api.aggregate(
        cuts=focus_cuts, drilldowns=focus_drilldowns)

    # Filter departments that belong to the selected government
    expenditure_results_filter_government_complete_breakdown = filter(
        lambda x: slugify(x[geo_ref]) == government_slug,
        expenditure_results['cells']
    )
    focus_results_filter_government = filter(
        lambda x: slugify(x[geo_ref]) == government_slug,
        focus_results['cells']
    )

    # Used to determine programmes for departments
    expenditure_results_filter_government_programme_breakdown = openspending_api.aggregate_by_refs(
        [
            department_ref,
            geo_ref,
            programme_ref,
        ],
        expenditure_results_filter_government_complete_breakdown
    )

    # Used to iterate over unique departments and build department objects
    expenditure_results_filter_government_department_breakdown = openspending_api.aggregate_by_refs(
        [
            department_ref,
            geo_ref,
        ],
        expenditure_results_filter_government_complete_breakdown
    )

    total_budget = 0
    filtered_result_cells = []
    sphere_depts = Department.objects.filter(
        government__sphere__financial_year__slug=financial_year_id,
        government__sphere__slug=sphere_slug,
        government__slug=government_slug,
        is_vote_primary=True,
    )

    for cell in expenditure_results_filter_government_department_breakdown:
        try:
            dept = sphere_depts.get(
                slug=slugify(cell[department_ref]),
                government__slug=slugify(cell[geo_ref])
            )
        except Department.DoesNotExist:
            logger.warning('Excluding: {} {} {} {}'.format(
                sphere_slug, financial_year_id, cell[geo_ref],
                cell[department_ref]
            ))
            continue

        total_budget += float(cell['value.sum'])
        cell['url'] = dept.get_url_path() if dept else None
        cell['description'] = dept.intro if dept else None
        filtered_result_cells.append(cell)

    for cell in filtered_result_cells:
        percentage_of_total = float(cell['value.sum']) / total_budget * 100

        department_programmes = filter(
            lambda x: x[department_ref] == cell[department_ref],
            expenditure_results_filter_government_programme_breakdown
        )
        programmes = []

        department_functions = filter(
            lambda x: x[department_ref] == cell[department_ref],
            focus_results_filter_government
        )
        functions = []

        for programme in department_programmes:
            percentage = float(
                programme['value.sum']) / cell['value.sum'] * 100
            programmes.append({
                'title': programme[programme_ref].title(),
                'slug': slugify(programme[programme_ref]),
                'percentage': percentage,
                'amount': float(programme['value.sum'])
            })

        for function in department_functions:
            slug = slugify(function[function_ref])
            if function[function_ref] == '':
                logger.error("Empty function object: {}".format(function))
            functions.append({
                'title': function[function_ref].title(),
                'slug': slug,
                'url': financial_year.get_focus_area_url(slug)
            })

        expenditure.append({
            'title': cell[department_ref],
            'slug': slugify(cell[department_ref]),
            'total': float(cell['value.sum']),
            'percentage_of_budget': percentage_of_total,
            'description': cell['description'],
            'programmes': programmes,
            'focus_areas': functions
        })

    return {
        'data': {'items': expenditure},
    } if expenditure else None
