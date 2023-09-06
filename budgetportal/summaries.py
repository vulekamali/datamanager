import logging

from slugify import slugify

from .datasets import (
    get_consolidated_expenditure_budget_dataset,
    get_expenditure_time_series_dataset,
)
from .models import (
    EXPENDITURE_TIME_SERIES_PHASE_MAPPING,
    Department,
    FinancialYear,
)
from .models.government import csv_url

logger = logging.getLogger(__name__)


PROV_EQ_SHARE_DEPT = "National Treasury"
PROV_EQ_SHARE_SUBPROG = "Provincial Equitable Share"


def get_focus_area_preview(financial_year):
    """Returns data for the focus area preview pages."""

    national_expenditure_results, national_os_api = get_focus_area_data(
        financial_year, "national"
    )
    provincial_expenditure_results, provincial_os_api = get_focus_area_data(
        financial_year, "provincial"
    )
    nat_function_ref = national_os_api.get_function_ref()
    prov_function_ref = provincial_os_api.get_function_ref()

    function_names = [cell[nat_function_ref] for cell in national_expenditure_results]
    function_names += [
        cell[prov_function_ref] for cell in provincial_expenditure_results
    ]
    unique_functions = list(set(function_names))

    function_objects = []
    for function in unique_functions:
        function_objects.append(
            {
                "title": function,
                "slug": slugify(function),
                "national": national_summary_for_function(
                    financial_year,
                    function,
                    national_os_api,
                    national_expenditure_results,
                ),
                "provincial": provincial_summary_for_function(
                    financial_year,
                    function,
                    provincial_os_api,
                    provincial_expenditure_results,
                ),
            }
        )
    function_objects.sort(key=lambda f: f["slug"])

    return {"data": {"items": function_objects}} if function_objects else None


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
        year_ref + ":" + "{}".format(financial_year.get_starting_year()),
        phase_ref + ":" + "{}".format("Main appropriation"),
    ]

    drilldowns = [function_ref, dept_ref]

    if sphere_slug == "provincial":
        drilldowns.append(government_ref)

    results = openspending_api.aggregate(cuts=cuts, drilldowns=drilldowns)
    cells = results["cells"]
    cells = [c for c in cells if c[function_ref] != ""]
    return cells, openspending_api


def get_prov_eq_share(financial_year):
    dataset = get_expenditure_time_series_dataset("national")
    if not dataset:
        return None, None
    openspending_api = dataset.get_openspending_api()
    year_ref = openspending_api.get_financial_year_ref()
    dept_ref = openspending_api.get_department_name_ref()
    function_ref = openspending_api.get_function_ref()
    phase_ref = openspending_api.get_phase_ref()
    subprogramme_ref = openspending_api.get_subprogramme_name_ref()

    cuts = [
        year_ref + ":" + "{}".format(financial_year.get_starting_year()),
        phase_ref + ":" + "{}".format("Main appropriation"),
        dept_ref + ":" + "{}".format(PROV_EQ_SHARE_DEPT),
        subprogramme_ref + ":" + "{}".format(PROV_EQ_SHARE_SUBPROG),
    ]

    drilldowns = [function_ref]

    results = openspending_api.aggregate(cuts=cuts, drilldowns=drilldowns)
    count = len(results["cells"])
    if count != 1:
        raise Exception(
            "Expected Provincial Equitable Share once but found it %d times" % count
        )
    cell = results["cells"][0]
    return (cell[function_ref], cell["value.sum"])


def national_summary_for_function(
    financial_year, function, openspending_api, expenditure_results
):
    eq_share_function, eq_share_amount = get_prov_eq_share(financial_year)

    dept_ref = openspending_api.get_department_name_ref()
    function_ref = openspending_api.get_function_ref()

    function_cells = [x for x in expenditure_results if x[function_ref] == function]
    national = {"data": [], "footnotes": [], "notices": []}
    national["total"] = sum(c["value.sum"] for c in function_cells)

    if not function_cells:
        notice = "No national departments allocated budget to this focus area."
        national["notices"].append(notice)
    national["footnotes"].append(
        "**Source:** Estimates of National Expenditure {}".format(financial_year.slug)
    )
    for cell in function_cells:
        if (
            cell[function_ref] == eq_share_function
            and cell[dept_ref] == PROV_EQ_SHARE_DEPT
        ):
            amount = cell["value.sum"] - eq_share_amount
            national["footnotes"].append(
                "**Note:** Provincial Equitable Share is excluded"
            )
        else:
            amount = cell["value.sum"]
        department_slug = slugify(cell[dept_ref])
        try:
            department = Department.objects.get(
                slug=department_slug,
                government__sphere__slug="national",
                government__sphere__financial_year=financial_year,
            )
            preview_url = department.get_preview_url_path()
        except Department.DoesNotExist:
            preview_url = None
        national["data"].append(
            {
                "title": cell[dept_ref],
                "slug": department_slug,
                "amount": amount,
                "url": preview_url,
            }
        )
    national["data"].sort(key=lambda x: x["slug"])
    return national


def provincial_summary_for_function(
    financial_year, function, openspending_api, expenditure_results
):
    dept_ref = openspending_api.get_department_name_ref()
    function_ref = openspending_api.get_function_ref()
    geo_ref = openspending_api.get_geo_ref()
    no_provincial_in_year = not expenditure_results

    function_cells = [x for x in expenditure_results if x[function_ref] == function]
    provincial = {"data": [], "footnotes": [], "notices": []}
    if no_provincial_in_year:
        provincial["total"] = None
    else:
        provincial["total"] = sum(c["value.sum"] for c in function_cells)

    if no_provincial_in_year:
        notice = (
            "Provincial budget allocations to focus areas "
            "for {} not published yet on vulekamali."
        ).format(financial_year.slug)
        provincial["notices"].append(notice)
    else:
        footnote = "**Source:** Estimates of Provincial Expenditure {}".format(
            financial_year.slug
        )
        provincial["footnotes"].append(footnote)

        if not function_cells:
            notice = "No provincial departments allocated budget to this focus area."
            provincial["notices"].append(notice)

        for cell in function_cells:
            department_slug = slugify(cell[dept_ref])
            try:
                department = Department.objects.get(
                    slug=department_slug,
                    government__name=cell[geo_ref],
                    government__sphere__slug="provincial",
                    government__sphere__financial_year=financial_year,
                )
                preview_url = department.get_preview_url_path()
            except Department.DoesNotExist:
                preview_url = None
            provincial["data"].append(
                {
                    "name": cell[dept_ref],
                    "slug": department_slug,
                    "amount": cell["value.sum"],
                    "url": preview_url,
                    "province": cell[geo_ref],
                }
            )
    provincial["data"].sort(key=lambda x: (x["province"], x["slug"]))
    return provincial


def get_focus_area_url_path(financial_year_slug, name):
    if name == "Contingency reserve":
        return None
    return "{}/focus/{}".format(financial_year_slug, slugify(name))


def get_consolidated_expenditure_treemap(financial_year):
    """Returns a data object for each function group for a specific year. Used by the consolidated treemap."""

    expenditure = []
    dataset = get_consolidated_expenditure_budget_dataset(financial_year)
    if not dataset:
        return None
    openspending_api = dataset.get_openspending_api()
    year_ref = openspending_api.get_financial_year_ref()

    # Add cuts: year and phase
    expenditure_cuts = [
        year_ref + ":" + "{}".format(financial_year.get_starting_year())
    ]
    expenditure_drilldowns = [openspending_api.get_function_ref()]

    expenditure_results = openspending_api.aggregate(
        cuts=expenditure_cuts, drilldowns=expenditure_drilldowns
    )

    total_budget = 0
    modified_result_cells = []

    for cell in expenditure_results["cells"]:
        total_budget += float(cell["value.sum"])
        modified_result_cells.append(cell)

    for cell in modified_result_cells:
        percentage_of_total = float(cell["value.sum"]) / total_budget * 100
        focus_area_name = cell[openspending_api.get_function_ref()]
        expenditure.append(
            {
                "name": focus_area_name,
                "id": slugify(cell[openspending_api.get_function_ref()]),
                "amount": float(cell["value.sum"]),
                "percentage": percentage_of_total,
                "url": get_focus_area_url_path(financial_year.slug, focus_area_name),
            }
        )

    return (
        {"data": {"items": expenditure, "total": total_budget}} if expenditure else None
    )


def get_preview_page(financial_year_id, phase_slug, government_slug, sphere_slug):
    try:
        selected_phase = EXPENDITURE_TIME_SERIES_PHASE_MAPPING[phase_slug]
    except KeyError:
        raise Exception("An invalid phase was provided: {}".format(phase_slug))

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
        openspending_api.get_adjustment_kind_ref() + ":" + '"Total"',
        openspending_api.get_financial_year_ref()
        + ":"
        + "{}".format(FinancialYear.start_from_year_slug(financial_year_id)),
        openspending_api.get_phase_ref() + ":" + '"{}"'.format(selected_phase),
    ]
    expenditure_drilldowns = [department_ref, geo_ref, programme_ref, function_ref]
    expenditure_results = openspending_api.aggregate(
        cuts=expenditure_cuts, drilldowns=expenditure_drilldowns
    )

    # We do a separate call to always build focus area data from the main
    # appropriation phase
    focus_cuts = [
        openspending_api.get_adjustment_kind_ref() + ":" + '"Total"',
        openspending_api.get_financial_year_ref()
        + ":"
        + "{}".format(FinancialYear.start_from_year_slug(financial_year_id)),
        openspending_api.get_phase_ref()
        + ":"
        + '"{}"'.format(EXPENDITURE_TIME_SERIES_PHASE_MAPPING["original"]),
    ]
    focus_drilldowns = [department_ref, geo_ref, function_ref]

    focus_results = openspending_api.aggregate(
        cuts=focus_cuts, drilldowns=focus_drilldowns
    )

    # Filter departments that belong to the selected government
    expenditure_results_filter_government_complete_breakdown = [
        x
        for x in expenditure_results["cells"]
        if slugify(x[geo_ref]) == government_slug
    ]
    focus_results_filter_government = [
        x for x in focus_results["cells"] if slugify(x[geo_ref]) == government_slug
    ]

    # Used to determine programmes for departments
    expenditure_results_filter_government_programme_breakdown = (
        openspending_api.aggregate_by_refs(
            [department_ref, geo_ref, programme_ref],
            expenditure_results_filter_government_complete_breakdown,
        )
    )

    # Used to iterate over unique departments and build department objects
    expenditure_results_filter_government_department_breakdown = (
        openspending_api.aggregate_by_refs(
            [department_ref, geo_ref],
            expenditure_results_filter_government_complete_breakdown,
        )
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
                government__slug=slugify(cell[geo_ref]),
            )
        except Department.DoesNotExist:
            logger.warning(
                "Excluding: {} {} {} {}".format(
                    sphere_slug, financial_year_id, cell[geo_ref], cell[department_ref]
                )
            )
            continue

        total_budget += float(cell["value.sum"])
        cell["url"] = dept.get_url_path() if dept else None
        cell["description"] = dept.intro if dept else None
        filtered_result_cells.append(cell)

    for cell in filtered_result_cells:
        percentage_of_total = float(cell["value.sum"]) / total_budget * 100

        department_programmes = [
            x
            for x in expenditure_results_filter_government_programme_breakdown
            if x[department_ref] == cell[department_ref]
        ]
        programmes = []

        department_functions = [
            x
            for x in focus_results_filter_government
            if x[department_ref] == cell[department_ref]
        ]
        functions = []

        for programme in department_programmes:
            percentage = float(programme["value.sum"]) / cell["value.sum"] * 100
            programmes.append(
                {
                    "title": programme[programme_ref].title(),
                    "slug": slugify(programme[programme_ref]),
                    "percentage": percentage,
                    "amount": float(programme["value.sum"]),
                }
            )

        for function in department_functions:
            name = function[function_ref]
            slug = slugify(name)
            functions.append(
                {
                    "title": name,
                    "slug": slug,
                    "url": get_focus_area_url_path(financial_year.slug, name),
                }
            )

        expenditure.append(
            {
                "title": cell[department_ref],
                "slug": slugify(cell[department_ref]),
                "total": float(cell["value.sum"]),
                "percentage_of_budget": percentage_of_total,
                "description": cell["description"],
                "programmes": programmes,
                "focus_areas": functions,
            }
        )

    return {"data": {"items": expenditure}} if expenditure else None


class DepartmentBudgetData(object):
    """
    An object that gathers all the bits for showing a data viz and its
    references and tools
    """

    def __init__(self, department):
        self.department = department

    def get_dataset(self):
        raise Exception("Not implemented")

    def get_openspending_api(self):
        dataset = self.get_dataset()
        if dataset is not None:
            return dataset.get_openspending_api()
        else:
            return None

    def get_model(self):
        return self.get_openspending_api().model

    def get_aggregate_cuts(self):
        raise Exception("Not implemented")

    def get_aggregate_drilldowns(self):
        raise Exception("Not implemented")

    def get_aggregate_url(self):
        openspending_api = self.get_openspending_api()
        return openspending_api.aggregate_url(
            cuts=self.get_aggregate_cuts(), drilldowns=self.get_aggregate_drilldowns()
        )

    def get_detail_aggregate_url(self):
        openspending_api = self.get_openspending_api()
        return openspending_api.aggregate_url(
            cuts=self.get_aggregate_cuts(),
            drilldowns=openspending_api.get_all_drilldowns(),
        )

    def get_detail_csv_url(self):
        return csv_url(self.get_detail_aggregate_url())


class DepartmentSubprogrammes(DepartmentBudgetData):
    def get_dataset(self):
        return self.department.get_estimates_of_subprogramme_expenditure_dataset()

    def get_aggregate_cuts(self):
        openspending_api = self.get_openspending_api()
        financial_year_start = self.department.get_financial_year().get_starting_year()
        cuts = [
            openspending_api.get_financial_year_ref() + ":" + financial_year_start,
            openspending_api.get_department_name_ref() + ":" + self.department.name,
            openspending_api.get_phase_ref() + ":" + "Main appropriation",
        ]
        if self.department.government.sphere.slug == "provincial":
            cuts.append(
                openspending_api.get_geo_ref()
                + ':"%s"' % self.department.government.name
            )
        return cuts

    def get_aggregate_drilldowns(self):
        openspending_api = self.get_openspending_api()
        return [
            openspending_api.get_programme_name_ref(),
            openspending_api.get_subprogramme_name_ref(),
        ]


class DepartmentSubprogEcon4(DepartmentBudgetData):
    def get_dataset(self):
        return self.department.get_estimates_of_econ_classes_expenditure_dataset(4)

    def get_aggregate_cuts(self):
        openspending_api = self.get_openspending_api()
        financial_year_start = self.department.get_financial_year().get_starting_year()
        cuts = [
            openspending_api.get_financial_year_ref() + ":" + financial_year_start,
            openspending_api.get_department_name_ref() + ":" + self.department.name,
            openspending_api.get_phase_ref() + ":" + "Main appropriation",
        ]
        if self.department.government.sphere.slug == "provincial":
            cuts.append(
                openspending_api.get_geo_ref()
                + ':"%s"' % self.department.government.name
            )
        return cuts

    def get_aggregate_drilldowns(self):
        openspending_api = self.get_openspending_api()
        return [
            openspending_api.get_programme_name_ref(),
            openspending_api.get_subprogramme_name_ref(),
            openspending_api.get_econ_class_4_ref(),
        ]


class DepartmentProgrammesEcon4(DepartmentBudgetData):
    def get_dataset(self):
        return self.department.get_estimates_of_econ_classes_expenditure_dataset(4)

    def get_aggregate_cuts(self):
        openspending_api = self.get_openspending_api()
        financial_year_start = self.department.get_financial_year().get_starting_year()
        cuts = [
            openspending_api.get_financial_year_ref() + ":" + financial_year_start,
            openspending_api.get_department_name_ref() + ":" + self.department.name,
            openspending_api.get_phase_ref() + ":" + "Main appropriation",
        ]
        if self.department.government.sphere.slug == "provincial":
            cuts.append(
                openspending_api.get_geo_ref()
                + ':"%s"' % self.department.government.name
            )
        return cuts

    def get_aggregate_drilldowns(self):
        openspending_api = self.get_openspending_api()
        return [
            openspending_api.get_programme_name_ref(),
            openspending_api.get_econ_class_4_ref(),
        ]


class BudgetedAndActualComparison(DepartmentBudgetData):
    def __init__(self, department):
        super().__init__(department)
        self.financial_year = None

    def get_dataset(self):
        return self.department.get_budgeted_and_actual_comparison_dataset(
            self.financial_year
        )

    def get_detail_aggregate_url(self):
        openspending_api = self.get_openspending_api()
        department_name = self.department.name
        if openspending_api is not None:
            department_ref = openspending_api.get_department_name_ref()
            cuts = [
                department_ref + ":" + "{}".format(department_name),
            ]
            aggregate_url = openspending_api.aggregate_url(cuts=cuts)

            return aggregate_url
        else:
            return None

    def get_detail_csv_urls(self):
        urls = {}
        for fy in FinancialYear.get_available_years():
            self.financial_year = fy.slug
            aggr_url = self.get_detail_aggregate_url()
            if aggr_url is not None:
                url = csv_url(aggr_url)
                urls[fy.slug] = url

        return urls
