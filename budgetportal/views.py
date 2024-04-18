import simplejson
import json
import logging
from csv import DictWriter
from datetime import datetime
from urllib.parse import unquote, urlparse

import requests
import yaml
from slugify import slugify

from budgetportal.csv_gen import generate_csv_response
from budgetportal.openspending import PAGE_SIZE
from django.conf import settings
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.forms.models import model_to_dict
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from haystack.query import SearchQuerySet
from constance import config

from .datasets import Category, Dataset
from .models import (
    FAQ,
    CategoryGuide,
    Department,
    Event,
    FinancialYear,
    Homepage,
    InfrastructureProjectPart,
    InYearMonitoringResourceLink,
    IRMSnapshot,
    MainMenuItem,
    PerformanceResourceLink,
    ProcurementResourceLink,
    Sphere,
    Video,
    ShowcaseItem,
)
from .models.government import PublicEntity, PublicEntityExpenditure
from .summaries import (
    InYearSpending,
    DepartmentProgrammesEcon4,
    DepartmentSubprogEcon4,
    DepartmentSubprogrammes,
    get_consolidated_expenditure_treemap,
    get_focus_area_preview,
    get_preview_page,
)
from .json_encoder import JSONEncoder

ckan = settings.CKAN

logger = logging.getLogger(__name__)

COMMON_DESCRIPTION = "South Africa's National and Provincial budget data "
COMMON_DESCRIPTION_ENDING = "from National Treasury in partnership with IMALI YETHU."


def serialize_showcase(showcase_items):
    showcase_items_dicts = [
        {
            "name": i.name,
            "description": i.description,
            "cta_text_1": i.cta_text_1,
            "cta_link_1": i.cta_link_1,
            "cta_text_2": i.cta_text_2,
            "cta_link_2": i.cta_link_2,
            "second_cta_type": i.second_cta_type,
            "thumbnail_url": i.file.url,
        }
        for i in showcase_items
    ]
    return json.dumps(
        showcase_items_dicts, cls=DjangoJSONEncoder, sort_keys=True, indent=4
    )


def homepage(request):
    year = FinancialYear.get_latest_year()
    titles = {
        "whyBudgetIsImportant",
        "howCanTheBudgetPortalHelpYou",
        "theBudgetProcess",
    }
    videos = Video.objects.filter(title_id__in=titles)

    page_data = Homepage.objects.first()
    latest_provincial_year = (
        FinancialYear.objects.filter(spheres__slug="provincial")
        .annotate(num_depts=Count("spheres__governments__departments"))
        .filter(num_depts__gt=0)
        .first()
    )

    showcase_items = ShowcaseItem.objects.all()

    context = {
        "selected_financial_year": None,
        "financial_years": [],
        "selected_tab": "homepage",
        "slug": year.slug,
        "title": "South African Government Budgets %s - vulekamali" % year.slug,
        "description": COMMON_DESCRIPTION + COMMON_DESCRIPTION_ENDING,
        "url_path": year.get_url_path(),
        "navbar": MainMenuItem.objects.prefetch_related("children").all(),
        "videos": videos,
        "latest_year": year.slug,
        "latest_provincial_year": latest_provincial_year
        and latest_provincial_year.slug,
        "main_heading": page_data.main_heading,
        "sub_heading": page_data.sub_heading,
        "primary_button_label": page_data.primary_button_label,
        "primary_button_url": page_data.primary_button_url,
        "secondary_button_label": page_data.secondary_button_label,
        "secondary_button_url": page_data.secondary_button_url,
        "call_to_action_sub_heading": page_data.call_to_action_sub_heading,
        "call_to_action_heading": page_data.call_to_action_heading,
        "call_to_action_link_label": page_data.call_to_action_link_label,
        "call_to_action_link_url": page_data.call_to_action_link_url,
        "showcase_items_json": serialize_showcase(showcase_items),
    }

    return render(request, "homepage.html", context)


def search_result(request, financial_year_id):
    slug = "search-result"
    context = {
        "financial_years": [],
        "selected_financial_year": financial_year_id,
        "selected_tab": None,
        "slug": slug,
        "title": "Search Results - vulekamali",
        "description": COMMON_DESCRIPTION + COMMON_DESCRIPTION_ENDING,
        "url_path": "/%s/%s" % (financial_year_id, slug),
    }

    for year in FinancialYear.get_available_years():
        is_selected = year.slug == financial_year_id
        context["financial_years"].append(
            {
                "id": year.slug,
                "is_selected": is_selected,
                "closest_match": {
                    "is_exact_match": True,
                    "url_path": "/%s/%s" % (year.slug, slug),
                },
            }
        )
    context["navbar"] = MainMenuItem.objects.prefetch_related("children").all()
    context["latest_year"] = FinancialYear.get_latest_year().slug
    return render(request, "search-result.html", context)


def programme_list_csv(request, financial_year_id, sphere_slug):
    sphere = get_object_or_404(
        Sphere, financial_year__slug=financial_year_id, slug=sphere_slug
    )
    filename = "programmes-%s-%s.csv" % (financial_year_id, sphere_slug)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="%s"' % filename
    fieldnames = [
        "government_name",
        "department_name",
        "programme_name",
        "programme_number",
    ]
    writer = DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    for government in sphere.governments.all():
        for department in government.departments.all():
            for programme in department.programmes.all():
                row = {
                    "government_name": government.name,
                    "department_name": department.name,
                    "programme_name": programme.name,
                    "programme_number": programme.programme_number,
                }
                writer.writerow(row)
    return response


def department_list_for_sphere_csv(request, financial_year_id, sphere_slug):
    get_object_or_404(Sphere, financial_year__slug=financial_year_id, slug=sphere_slug)
    return department_list_csv(request, financial_year_id, [sphere_slug])


def department_list_csv(request, financial_year_id, spheres=["national", "provincial"]):
    selected_year = get_object_or_404(FinancialYear, slug=financial_year_id)

    filename = "departments-%s.csv" % (financial_year_id)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="%s"' % filename

    fieldnames = [
        "government",
        "department_name",
        "vote_number",
        "is_vote_primary",
        "intro",
        "website_url",
    ]
    writer = DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    for sphere_name in spheres:
        for government in (
            selected_year.spheres.filter(slug=sphere_name).first().governments.all()
        ):
            for department in government.departments.all():
                writer.writerow(
                    {
                        "government": government.name,
                        "department_name": department.name,
                        "vote_number": department.vote_number,
                        "is_vote_primary": department.is_vote_primary,
                        "intro": department.intro,
                        "website_url": department.get_latest_website_url(),
                    }
                )

    return response


def department_list_data(financial_year_id):
    selected_year = get_object_or_404(FinancialYear, slug=financial_year_id)
    page_data = {
        "financial_years": [],
        "selected_financial_year": selected_year.slug,
        "selected_tab": "departments",
        "slug": "departments",
        "title": "Department Budgets for %s - vulekamali" % selected_year.slug,
        "description": "Department budgets for the %s financial year %s"
        % (selected_year.slug, COMMON_DESCRIPTION_ENDING),
    }

    for year in FinancialYear.get_available_years():
        is_selected = year.slug == financial_year_id
        page_data["financial_years"].append(
            {
                "id": year.slug,
                "is_selected": is_selected,
                "closest_match": {
                    "is_exact_match": True,
                    "url_path": "/%s/departments" % year.slug,
                },
            }
        )

    for sphere_name in ("national", "provincial"):
        page_data[sphere_name] = []
        for government in (
            selected_year.spheres.filter(slug=sphere_name).first().governments.all()
        ):
            departments = []
            for department in government.departments.all():
                departments.append(
                    {
                        "name": department.name,
                        "slug": str(department.slug),
                        "vote_number": department.vote_number,
                        "url_path": department.get_url_path(),
                        "website_url": department.get_latest_website_url(),
                    }
                )
            departments = sorted(departments, key=lambda d: d["vote_number"])
            page_data[sphere_name].append(
                {
                    "name": government.name,
                    "slug": str(government.slug),
                    "departments": departments,
                }
            )

    return page_data


def public_entity_list_data(financial_year_id):
    selected_year = get_object_or_404(FinancialYear, slug=financial_year_id)
    page_data = {
        "financial_years": [],
        "selected_financial_year": selected_year.slug,
        "selected_tab": "public_entities",
        "slug": "public-entities",
        "title": "Public Entities Budgets for %s - vulekamali" % selected_year.slug,
        "public_entities": [],
        "description": "Public Entities budgets for the %s financial year %s"
        % (selected_year.slug, COMMON_DESCRIPTION_ENDING),
    }

    for year in FinancialYear.get_available_years():
        is_selected = year.slug == financial_year_id
        page_data["financial_years"].append(
            {
                "id": year.slug,
                "is_selected": is_selected,
                "closest_match": {
                    "is_exact_match": True,
                    "url_path": "/%s/public-entities" % year.slug,
                },
            }
        )

    for government in (
        selected_year.spheres.filter(slug="national").first().governments.all()
    ):
        public_entities = []
        for public_entity in government.public_entities.all():
            public_entities.append(
                {
                    "name": public_entity.name,
                    "url_path": public_entity.get_url_path(),
                    "department": public_entity.department.name,
                    "department_slug": public_entity.department.slug,
                    "department_sphere": public_entity.department.government.sphere.slug,
                    "functiongroup1": public_entity.functiongroup1,
                    "selected_year_slug": selected_year.slug,
                    "pfma": public_entity.pfma,
                    "amount": int(public_entity.amount),
                }
            )
        public_entities = sorted(public_entities, key=lambda d: d["name"])
        page_data["public_entities"].append(public_entities)

    page_data["public_entities"] = [
        item for sublist in page_data["public_entities"] for item in sublist
    ]

    return page_data


def department_page(
    request, financial_year_id, sphere_slug, government_slug, department_slug
):
    department = None
    selected_year = get_object_or_404(FinancialYear, slug=financial_year_id)

    years = FinancialYear.get_available_years()
    for year in years:
        if year.slug == financial_year_id:
            selected_year = year
            sphere = selected_year.spheres.filter(slug=sphere_slug).first()
            government = sphere.governments.filter(slug=government_slug).first()
            department = government.departments.filter(slug=department_slug).first()

    financial_years_context = []
    for year in years:
        closest_match, closest_is_exact = year.get_closest_match(department)
        financial_years_context.append(
            {
                "id": year.slug,
                "is_selected": year.slug == financial_year_id,
                "closest_match": {
                    "url_path": closest_match.get_url_path(),
                    "is_exact_match": closest_is_exact,
                },
            }
        )

    contributed_datasets = []
    for dataset in department.get_contributed_datasets():
        contributed_datasets.append(
            {
                "name": dataset.name,
                "contributor": dataset.get_organization()["name"],
                "url_path": dataset.get_url_path(),
            }
        )

    # ======= main budget docs =========================
    budget_dataset = department.get_dataset(group_name="budget-vote-documents")
    if budget_dataset:
        document_resource = budget_dataset.get_resource(format="PDF")
        if document_resource:
            document_resource = resource_fields(document_resource)
        tables_resource = budget_dataset.get_resource(
            format="XLS"
        ) or budget_dataset.get_resource(format="XLSX")
        if tables_resource:
            tables_resource = resource_fields(tables_resource)
        department_budget = {
            "name": budget_dataset.name,
            "document": document_resource,
            "tables": tables_resource,
        }
    else:
        department_budget = None

    # ======= adjusted budget docs =========================
    adjusted_budget_dataset = department.get_dataset(
        group_name="adjusted-budget-vote-documents"
    )
    if adjusted_budget_dataset:
        document_resource = adjusted_budget_dataset.get_resource(format="PDF")
        if document_resource:
            document_resource = resource_fields(document_resource)
        tables_resource = adjusted_budget_dataset.get_resource(
            format="XLS"
        ) or adjusted_budget_dataset.get_resource(format="XLSX")
        if tables_resource:
            tables_resource = resource_fields(tables_resource)
        department_adjusted_budget = {
            "name": adjusted_budget_dataset.name,
            "document": document_resource,
            "tables": tables_resource,
        }
    else:
        department_adjusted_budget = None

    primary_department = department.get_primary_department()

    if department.government.sphere.slug == "national":
        govt_label = "National"
    elif department.government.sphere.slug == "provincial":
        govt_label = department.government.name

    context = {
        "comments_enabled": settings.COMMENTS_ENABLED,
        "subprogramme_viz_data": DepartmentSubprogrammes(department),
        "subprog_treemap_url": get_viz_url(
            department, "department-viz-subprog-treemap"
        ),
        "prog_econ4_circles_data": DepartmentProgrammesEcon4(department),
        "prog_econ4_circles_url": get_viz_url(
            department, "department-viz-subprog-econ4-circles"
        ),
        "subprog_econ4_bars_data": DepartmentSubprogEcon4(department),
        "subprog_econ4_bars_url": get_viz_url(
            department, "department-viz-subprog-econ4-bars"
        ),
        "expenditure_over_time": department.get_expenditure_over_time(),
        "budget_actual": department.get_expenditure_time_series_summary(),
        "budget_actual_programmes": department.get_expenditure_time_series_by_programme(),
        "adjusted_budget_summary": department.get_adjusted_budget_summary(),
        "contributed_datasets": contributed_datasets if contributed_datasets else None,
        "financial_years": financial_years_context,
        "government": {
            "name": department.government.name,
            "label": govt_label,
            "slug": str(department.government.slug),
        },
        "government_functions": [f.name for f in department.get_govt_functions()],
        "intro": department.intro,
        "infra_enabled": IRMSnapshot.objects.filter(
            sphere__slug=department.government.sphere.slug
        ).count(),
        "is_vote_primary": department.is_vote_primary,
        "name": department.name,
        "projects": get_department_project_summary(govt_label, department),
        "slug": str(department.slug),
        "sphere": {
            "name": department.government.sphere.name,
            "slug": department.government.sphere.slug,
        },
        "selected_financial_year": financial_year_id,
        "selected_tab": "departments",
        "title": "%s budget %s  - vulekamali" % (department.name, selected_year.slug),
        "description": "%s department: %s budget data for the %s financial year %s"
        % (
            govt_label,
            department.name,
            selected_year.slug,
            COMMON_DESCRIPTION_ENDING,
        ),
        "department_budget": department_budget,
        "department_adjusted_budget": department_adjusted_budget,
        "procurement_resource_links": ProcurementResourceLink.objects.filter(
            sphere_slug__in=(
                "all",
                department.government.sphere.slug,
            )
        ),
        "performance_resource_links": PerformanceResourceLink.objects.filter(
            sphere_slug__in=(
                "all",
                department.government.sphere.slug,
            )
        ),
        "in_year_monitoring_resource_links": InYearMonitoringResourceLink.objects.filter(
            sphere_slug__in=(
                "all",
                department.government.sphere.slug,
            )
        ),
        "vote_number": department.vote_number,
        "vote_primary": {
            "url_path": primary_department.get_url_path(),
            "name": primary_department.name,
            "slug": primary_department.slug,
        },
        "website_url": department.get_latest_website_url(),
    }
    context["navbar"] = MainMenuItem.objects.prefetch_related("children").all()
    context["latest_year"] = FinancialYear.get_latest_year().slug
    context["global_values"] = read_object_from_yaml(
        str(settings.ROOT_DIR.path("_data/global_values.yaml"))
    )
    context["admin_url"] = reverse(
        "admin:budgetportal_department_change", args=(department.pk,)
    )
    context["eqprs_data_enabled"] = config.EQPRS_DATA_ENABLED
    context["in_year_spending_enabled"] = config.IN_YEAR_SPENDING_ENABLED
    context["budgeted_and_actual_comparison"] = get_in_year_spending_urls(
        department, financial_years_context
    )

    context["public_entities"] = []

    for public_entity in PublicEntity.objects.filter(
        department__slug=department_slug, government=department.government
    ):
        context["public_entities"].append(
            {
                "name": public_entity.name,
                "url_path": public_entity.get_url_path(),
            }
        )

    return render(request, "department.html", context)


def public_entity_page(
    request, financial_year_id, sphere_slug, government_slug, public_entity_slug
):
    # Get public entity by public_entity_slug
    selected_public_entity = PublicEntity.objects.filter(
        slug=public_entity_slug
    ).first()
    selected_year = get_object_or_404(FinancialYear, slug=financial_year_id)

    # Total up public entityies amount
    total_amount = 0
    for government in (
        selected_year.spheres.filter(slug="national").first().governments.all()
    ):
        for public_entity in government.public_entities.all():
            total_amount += public_entity.amount

    # Total up public entities in same department
    total_department_amount = 0
    department_public_entities = []
    chart_data = []
    for department_public_entity in PublicEntity.objects.filter(
        department=selected_public_entity.department
    ):
        total_department_amount += department_public_entity.amount
        department_public_entities.append(department_public_entity)
        # if department_public_entity is selected_public_entity then color_group = 2 else 1
        colour_group = 2 if department_public_entity == selected_public_entity else 1
        chart_data.append(
            [
                colour_group,
                simplejson.dumps(department_public_entity.amount, use_decimal=True),
                department_public_entity.name,
                simplejson.dumps(department_public_entity.id),
                department_public_entity.slug,
            ]
        )

    # Get public entity expenditure
    public_entity_expenditure = PublicEntityExpenditure.objects.filter(
        public_entity=selected_public_entity
    )

    # Public entity amount percentage of total department amount
    percentage_of_total_department_amount = (
        selected_public_entity.amount / total_department_amount
    ) * 100

    # Public entity amount percentage of total amount
    percentage_of_total_amount = (selected_public_entity.amount / total_amount) * 100

    context = {
        "public_entity_id": selected_public_entity.id,
        "intro": selected_public_entity.intro,
        "name": selected_public_entity.name,
        "department": selected_public_entity.department.name,
        "department_slug": selected_public_entity.department.slug,
        "slug": str(selected_public_entity.slug),
        "selected_financial_year": financial_year_id,
        "selected_tab": "public_entities",
        "title": "%s expenditure %s  - vulekamali"
        % (selected_public_entity.name, selected_year.slug),
        "description": "%s public entity: Expenditure data for the %s financial year %s"
        % (
            selected_public_entity.name,
            selected_year.slug,
            COMMON_DESCRIPTION_ENDING,
        ),
        "public_entity": selected_public_entity,
        "total_amount": total_amount,
        "total_department_amount": total_department_amount,
        "percentage_of_total_amount": percentage_of_total_amount,
        "percentage_of_total_department_amount": percentage_of_total_department_amount,
        "department_public_entities": department_public_entities,
        "chart_data": chart_data,
        "public_entity_expenditure": public_entity_expenditure,
    }
    context["navbar"] = MainMenuItem.objects.prefetch_related("children").all()
    context["latest_year"] = FinancialYear.get_latest_year().slug
    context["global_values"] = read_object_from_yaml(
        str(settings.ROOT_DIR.path("_data/global_values.yaml"))
    )
    context["admin_url"] = reverse(
        "admin:budgetportal_department_change", args=(selected_public_entity.pk,)
    )

    return render(request, "public_entity.html", context)


def get_in_year_spending_urls(department, financial_years):
    urls = {}

    for fy in financial_years:
        department_obj = Department.objects.filter(
            name=department.name,
            government__sphere__slug="national",
            government__sphere__financial_year__slug=fy["id"],
        ).first()
        year = fy["id"]
        comparison_obj = InYearSpending(department_obj)
        urls[year] = comparison_obj.get_detail_csv_url()

    return urls


def get_department_project_summary(government_label, department):
    return (
        SearchQuerySet()
        .filter(government_label=government_label, department=department.name)
        .order_by("-estimated_total_project_cost")[:10]
    )


def get_viz_url(department, url_name_suffix):
    if department.government.sphere.slug == "national":
        return reverse(
            "national:" + url_name_suffix,
            args=[department.government.sphere.financial_year.slug, department.slug],
        )
    elif department.government.sphere.slug == "provincial":
        return reverse(
            "provincial:" + url_name_suffix,
            args=[
                department.government.sphere.financial_year.slug,
                department.government.sphere.slug,
                department.government.slug,
                department.slug,
            ],
        )


def get_department_by_slugs(
    financial_year_id, sphere_slug, government_slug, department_slug
):
    return get_object_or_404(
        Department,
        slug=department_slug,
        government__slug=government_slug,
        government__sphere__slug=sphere_slug,
        government__sphere__financial_year__slug=financial_year_id,
    )


def department_viz_subprog_treemap(
    request, financial_year_id, sphere_slug, government_slug, department_slug
):
    department = get_department_by_slugs(
        financial_year_id, sphere_slug, government_slug, department_slug
    )
    context = {"viz_data": DepartmentSubprogrammes(department)}
    return render(request, "department_viz_subprogrammes.html", context)


def department_viz_subprog_econ4_circles(
    request, financial_year_id, sphere_slug, government_slug, department_slug
):
    department = get_department_by_slugs(
        financial_year_id, sphere_slug, government_slug, department_slug
    )
    context = {"viz_data": DepartmentProgrammesEcon4(department)}
    return render(request, "department_viz_subprog_econ4_circles.html", context)


def department_viz_subprog_econ4_bars(
    request, financial_year_id, sphere_slug, government_slug, department_slug
):
    department = get_department_by_slugs(
        financial_year_id, sphere_slug, government_slug, department_slug
    )
    context = {"viz_data": DepartmentSubprogEcon4(department)}
    return render(request, "department_viz_subprog_econ4_bars.html", context)


def infrastructure_projects_overview(request):
    """Overview page to showcase all featured infrastructure projects"""
    infrastructure_projects = InfrastructureProjectPart.objects.filter(
        featured=True
    ).distinct("project_slug")
    if infrastructure_projects is None:
        raise Http404()
    projects = []
    for project in infrastructure_projects:
        departments = Department.objects.filter(
            slug=slugify(project.government_institution),
            government__sphere__slug="national",
        )
        department_url = None
        if departments:
            department_url = (
                departments[0].get_latest_department_instance().get_url_path()
            )
        projects.append(
            {
                "name": project.project_name,
                "coordinates": project.clean_coordinates(project.gps_code),
                "projected_budget": project.calculate_projected_expenditure(),
                "stage": project.current_project_stage,
                "description": project.project_description,
                "provinces": project.provinces.split(","),
                "total_budget": project.project_value_rands,
                "detail": project.get_url_path(),
                "slug": project.get_url_path(),
                "page_title": "{} - vulekamali".format(project.project_name),
                "government_institution": {
                    "name": project.government_institution,
                    "url": department_url,
                },
                "nature_of_investment": project.nature_of_investment,
                "infrastructure_type": project.infrastructure_type,
                "expenditure": sorted(
                    project.build_complete_expenditure(), key=lambda e: e["year"]
                ),
                "administration_type": project.administration_type,
                "partnership_type": project.partnership_type,
                "date_of_close": project.date_of_close,
                "duration": project.duration,
                "financing_structure": project.financing_structure,
                "project_value_rand_million": project.project_value_rand_million,
                "form_of_payment": project.form_of_payment,
            }
        )
    projects = sorted(projects, key=lambda p: p["name"])
    return {
        "dataset_url": reverse("dataset-category", args=("infrastructure-projects",)),
        "projects": projects,
        "description": "National department Infrastructure projects in South Africa",
        "slug": "infrastructure-projects",
        "selected_tab": "infrastructure-projects",
        "title": "Infrastructure Projects - vulekamali",
    }


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
        "site": {"latest_year": FinancialYear.get_latest_year().slug},
    }
    return render(request, "infrastructure_project_list.html", context)


def infrastructure_project_detail_data(project_slug):
    project = InfrastructureProjectPart.objects.filter(
        project_slug=project_slug
    ).first()
    if not project:
        return HttpResponse(status=404)

    departments = Department.objects.filter(
        slug=slugify(project.government_institution),
        government__sphere__slug="national",
    )
    department_url = None
    if departments:
        department_url = departments[0].get_latest_department_instance().get_url_path()
    dataset_url = reverse("dataset-category", args=("infrastructure-projects",))

    project_dict = {
        "name": project.project_name,
        "coordinates": project.clean_coordinates(project.gps_code),
        "projected_budget": project.calculate_projected_expenditure(),
        "stage": project.current_project_stage,
        "description": project.project_description,
        "provinces": project.provinces.split(","),
        "total_budget": project.project_value_rands,
        "detail": project.get_url_path(),
        "dataset_url": dataset_url,
        "slug": project.get_url_path(),
        "page_title": "{} - vulekamali".format(project.project_name),
        "government_institution": {
            "name": project.government_institution,
            "url": department_url,
        },
        "nature_of_investment": project.nature_of_investment,
        "infrastructure_type": project.infrastructure_type,
        "expenditure": sorted(
            project.build_complete_expenditure(), key=lambda e: e["year"]
        ),
        "administration_type": project.administration_type,
        "partnership_type": project.partnership_type,
        "date_of_close": project.date_of_close,
        "duration": project.duration,
        "financing_structure": project.financing_structure,
        "project_value_rand_million": project.project_value_rand_million,
        "form_of_payment": project.form_of_payment,
    }
    return {
        "dataset_url": dataset_url,
        "projects": [project_dict],
        "description": project.project_description
        or "Infrastructure projects in South Africa",
        "slug": "infrastructure-projects",
        "selected_tab": "infrastructure-projects",
        "title": f"{project.project_name} - Infrastructure Projects - vulekamali",
    }


def infrastructure_project_detail_json(request, project_slug):
    response = infrastructure_project_detail_data(project_slug)
    # For 404 - not sure why not raising a 404 exception.
    if isinstance(response, HttpResponse):
        return response

    response_json = json.dumps(
        response, sort_keys=True, indent=4, separators=(",", ": ")
    )
    return HttpResponse(response_json, content_type="application/json")


def infrastructure_project_detail(request, project_slug):
    dataset_response = infrastructure_project_detail_data(project_slug)
    # For 404 - not sure why not raising a 404 exception.
    if isinstance(dataset_response, HttpResponse):
        return dataset_response
    latest_year_slug = FinancialYear.get_latest_year().slug

    context = {
        "page": {"layout": "infrastructure_project", "data_key": "dataset"},
        "site": {
            "data": {
                "navbar": MainMenuItem.objects.prefetch_related("children").all(),
                "dataset": dataset_response,
            },
            "latest_year": latest_year_slug,
        },
        "debug": settings.DEBUG,
    }
    return render(request, "infrastructure_project.html", context)


def openspending_csv(request):
    """
    Ensure that API call is to OpenSpending *
    Get result from API call
    Feed dict result to CSV generator
    Return streaming http response
    :param request: HttpRequest
    :return: StreamingHttpResponse
    """
    api_url = unquote(str(request.GET.get("api_url")))

    parsed_url = urlparse(api_url)
    domain = "{uri.netloc}".format(uri=parsed_url)
    allowed_domains = {
        "openspending.org",
        "openspending.vulekamali.gov.za",
        "openspending-dedicated.vulekamali.gov.za",
    }
    if domain not in allowed_domains:
        return HttpResponse(
            "Invalid domain received: %s (Only openspending.org is allowed)" % domain,
            status=403,
        )

    result = requests.get(api_url)
    logger.info("request %s took %dms", api_url, result.elapsed.microseconds / 1000)
    result.raise_for_status()
    if result.json()["total_cell_count"] > PAGE_SIZE:
        raise Exception("More cells than expected - perhaps we should start paging")
    return generate_csv_response(result.json())


def dataset_fields(dataset):
    return {
        "slug": dataset.slug,
        "name": dataset.name,
        "resources": [resource_fields(r) for r in dataset.resources],
        "organization": dataset.get_organization(),
        "author": dataset.author,
        "created": dataset.created_date,
        "last_updated": dataset.last_updated_date,
        "license": dataset.license,
        "intro": dataset.intro,
        "intro_short": dataset.intro_short,
        "key_points": dataset.key_points,
        "importance": dataset.importance,
        "use_for": dataset.use_for,
        "usage": dataset.usage,
        "methodology": dataset.methodology,
        "url_path": dataset.get_url_path(),
        "category": category_fields(dataset.category),
    }


def resource_fields(resource):
    return {
        "name": resource["name"],
        "url": resource["url"],
        "description": resource["description"],
        "format": resource["format"],
    }


def category_fields(category):
    return {
        "name": category.name,
        "slug": category.slug,
        "url_path": category.get_url_path(),
        "description": category.description,
    }


def about(request):
    context = {
        "title": "About - vulekamali",
        "description": COMMON_DESCRIPTION + COMMON_DESCRIPTION_ENDING,
        "selected_tab": "about",
        "selected_financial_year": None,
        "financial_years": [],
        "video": Video.objects.get(title_id="onlineBudgetPortal"),
        "navbar": MainMenuItem.objects.prefetch_related("children").all(),
        "latest_year": FinancialYear.get_latest_year().slug,
    }
    return render(request, "about.html", context)


def static_search_data(request):
    glossary_data_file_path = str(settings.ROOT_DIR.path("_data/glossary.json"))
    with open(glossary_data_file_path) as glossary_file:
        glossary_data = json.load(glossary_file)
    context = {
        "videos": [model_to_dict(v) for v in Video.objects.all()],
        "glossary": glossary_data,
    }

    response_json = json.dumps(
        context, sort_keys=True, indent=4, separators=(",", ": "), cls=DjangoJSONEncoder
    )
    return HttpResponse(response_json, content_type="application/json")


def events(request):
    upcoming_events = Event.objects.filter(status="upcoming")
    past_events = Event.objects.filter(status="past")

    context = {
        "page": {"layout": "events", "data_key": "events"},
        "site": {
            "data": {
                "events": {"upcoming": upcoming_events, "past": past_events},
                "navbar": MainMenuItem.objects.prefetch_related("children").all(),
            },
            "latest_year": FinancialYear.get_latest_year().slug,
        },
        "debug": settings.DEBUG,
    }
    return render(request, "events.html", context)


def glossary(request):
    context = {
        "navbar": MainMenuItem.objects.prefetch_related("children").all(),
        "selected_tab": "learning-centre",
        "selected_sidebar": "glossary",
        "title": "Glossary - vulekamali",
        "description": COMMON_DESCRIPTION + COMMON_DESCRIPTION_ENDING,
        "latest_year": FinancialYear.get_latest_year().slug,
        "selected_financial_year": None,
        "financial_years": [],
    }
    return render(request, "glossary.html", context)


def faq(request):
    faq_list = FAQ.objects.all()
    context = {
        "navbar": MainMenuItem.objects.prefetch_related("children").all(),
        "title": "FAQ - vulekamali",
        "description": COMMON_DESCRIPTION + COMMON_DESCRIPTION_ENDING,
        "selected_tab": "faq",
        "latest_year": FinancialYear.get_latest_year().slug,
        "selected_financial_year": None,
        "financial_years": [],
        "faq_list": faq_list,
    }
    return render(request, "faq.html", context)


def videos(request):
    context = {
        "title": "Videos - vulekamali",
        "description": COMMON_DESCRIPTION + COMMON_DESCRIPTION_ENDING,
        "selected_tab": "learning-centre",
        "selected_sidebar": "videos",
        "videos": Video.objects.all(),
        "navbar": MainMenuItem.objects.prefetch_related("children").all(),
        "latest_year": FinancialYear.get_latest_year().slug,
        "admin_url": reverse("admin:budgetportal_video_changelist"),
    }
    return render(request, "videos.html", context)


def terms_and_conditions(request):
    context = {
        "title": "Terms of use - vulekamali",
        "description": COMMON_DESCRIPTION + COMMON_DESCRIPTION_ENDING,
        "navbar": MainMenuItem.objects.prefetch_related("children").all(),
        "latest_year": FinancialYear.get_latest_year().slug,
    }
    return render(request, "terms-and-conditions.html", context)


def resources(request):
    titles = {"theBudgetProcess", "participate"}

    context = {
        "navbar": MainMenuItem.objects.prefetch_related("children").all(),
        "videos": Video.objects.filter(title_id__in=titles),
        "latest_year": FinancialYear.get_latest_year().slug,
        "title": "Resources - vulekamali",
        "description": COMMON_DESCRIPTION + COMMON_DESCRIPTION_ENDING,
        "selected_tab": "learning-centre",
        "selected_sidebar": "resources",
    }
    return render(request, "resources.html", context)


def dataset_category_list_page(request):
    context = {
        "categories": [category_fields(c) for c in Category.get_all()],
        "selected_tab": "datasets",
        "slug": "datasets",
        "name": "Datasets and Analysis",
        "title": "Datasets and Analysis - vulekamali",
        "url_path": "/datasets",
        "navbar": MainMenuItem.objects.prefetch_related("children").all(),
        "latest_year": FinancialYear.get_latest_year().slug,
    }

    return render(request, "datasets.html", context)


def dataset_category_context(category_slug):
    category = Category.get_by_slug(category_slug)
    context = {
        "datasets": [],
        "selected_tab": "datasets",
        "slug": category.slug,
        "name": category.name,
        "title": "%s - vulekamali" % category.name,
        "description": category.description,
        "url_path": category.get_url_path(),
    }

    for dataset in category.get_datasets():
        field_subset = dataset_fields(dataset)
        field_subset["description"] = field_subset.pop("intro")
        field_subset["created"] = datetime.strptime(
            field_subset["created"], "%Y-%m-%dT%H:%M:%S.%f"
        )
        field_subset["last_updated"] = datetime.strptime(
            field_subset["last_updated"], "%Y-%m-%dT%H:%M:%S.%f"
        )
        del field_subset["methodology"]
        del field_subset["key_points"]
        del field_subset["use_for"]
        del field_subset["usage"]
        del field_subset["importance"]
        context["datasets"].append(field_subset)

    return context


def dataset_category_page(request, category_slug):
    context = dataset_category_context(category_slug)
    context["navbar"] = MainMenuItem.objects.prefetch_related("children").all()
    context["latest_year"] = FinancialYear.get_latest_year().slug
    context["guide"] = CategoryGuide.objects.filter(category_slug=category_slug).first()
    return render(request, "government_dataset_category.html", context)


def contributed_datasets_list(request):
    context = dataset_category_context("contributed")
    context["navbar"] = MainMenuItem.objects.prefetch_related("children").all()
    context["latest_year"] = FinancialYear.get_latest_year().slug
    return render(request, "contributed_data_category.html", context)


def dataset_context(category_slug, dataset_slug):
    dataset = Dataset.fetch(dataset_slug)
    assert dataset.category.slug == category_slug

    if category_slug == "contributed":
        description = (
            "Data and/or documentation related to South African"
            " government budgets contributed by %s and hosted"
            " by National Treasury in partnership with IMALI YETHU"
        ) % dataset.get_organization()["name"]
    else:
        description = dataset.intro

    context = {
        "selected_tab": "datasets",
        "title": "%s - vulekamali" % dataset.name,
        "description": description,
    }

    context.update(dataset_fields(dataset))
    return context


def dataset_page(request, category_slug, dataset_slug):
    context = dataset_context(category_slug, dataset_slug)
    context["navbar"] = MainMenuItem.objects.prefetch_related("children").all()
    context["latest_year"] = FinancialYear.get_latest_year().slug
    context["created"] = datetime.strptime(context["created"], "%Y-%m-%dT%H:%M:%S.%f")
    context["last_updated"] = datetime.strptime(
        context["last_updated"], "%Y-%m-%dT%H:%M:%S.%f"
    )
    external_resource_slugs = [
        "socio-economic-data",
        "performance-resources",
        "procurement-portals-and-resources",
    ]
    context["guide"] = CategoryGuide.objects.filter(category_slug=category_slug).first()
    context["external_resource_page"] = category_slug in external_resource_slugs
    context["comments_enabled"] = settings.COMMENTS_ENABLED
    return render(request, "government_dataset.html", context)


def contributed_dataset(request, dataset_slug):
    context = dataset_context("contributed", dataset_slug)
    context["navbar"] = MainMenuItem.objects.prefetch_related("children").all()
    context["latest_year"] = FinancialYear.get_latest_year().slug
    context["created"] = datetime.strptime(context["created"], "%Y-%m-%dT%H:%M:%S.%f")
    context["last_updated"] = datetime.strptime(
        context["last_updated"], "%Y-%m-%dT%H:%M:%S.%f"
    )
    context["comments_enabled"] = settings.COMMENTS_ENABLED
    return render(request, "contributed_dataset.html", context)


def latest_department_list(request):
    url = reverse("department-list", args=(FinancialYear.get_latest_year().slug,))
    return redirect(url, permanent=False)


def department_list(request, financial_year_id):
    context = department_list_data(financial_year_id)
    context["navbar"] = MainMenuItem.objects.prefetch_related("children").all()
    context["latest_year"] = FinancialYear.get_latest_year().slug
    return render(request, "department_list.html", context)


def latest_public_entity_list(request):
    department = request.GET.get("department", None)
    url = reverse("public-entity-list", args=(FinancialYear.get_latest_year().slug,))
    url = f"{url}?department={department}" if department else url
    return redirect(url, permanent=False)


def public_entity_list(request, financial_year_id):
    context = public_entity_list_data(financial_year_id)
    context["navbar"] = MainMenuItem.objects.prefetch_related("children").all()
    context["latest_year"] = FinancialYear.get_latest_year().slug
    return render(request, "public_entity_list.html", context)


def department_list_json(request, financial_year_id):
    response_json = json.dumps(
        department_list_data(financial_year_id),
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
        cls=DjangoJSONEncoder,
    )
    return HttpResponse(response_json, content_type="application/json")


def treemaps_data(financial_year_id, phase_slug, sphere_slug):
    """The data for the vulekamali home page treemaps"""
    dept = Department.objects.filter(government__sphere__slug=sphere_slug)[0]
    if sphere_slug == "national":
        page_data = dept.get_national_expenditure_treemap(financial_year_id, phase_slug)
    elif sphere_slug == "provincial":
        page_data = dept.get_provincial_expenditure_treemap(
            financial_year_id, phase_slug
        )
    else:
        return HttpResponse("Unknown government sphere.", status=400)
    return page_data


def treemaps_json(request, financial_year_id, phase_slug, sphere_slug):
    response_json = json.dumps(
        treemaps_data(financial_year_id, phase_slug, sphere_slug),
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )
    return HttpResponse(response_json, content_type="application/json")


def consolidated_treemap(financial_year_id):
    """The data for the vulekamali home page treemaps"""
    financial_year = FinancialYear.objects.get(slug=financial_year_id)
    page_data = get_consolidated_expenditure_treemap(financial_year)
    if page_data is None:
        raise Http404()
    return page_data


def consolidated_treemap_json(request, financial_year_id):
    response_json = json.dumps(
        consolidated_treemap(financial_year_id),
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )
    return HttpResponse(response_json, content_type="application/json")


def focus_preview_data(financial_year_id):
    """The data for the focus area preview pages for a specific year"""
    financial_year = FinancialYear.objects.get(slug=financial_year_id)
    page_data = get_focus_area_preview(financial_year)
    return page_data


def focus_preview_json(request, financial_year_id):
    response_json = json.dumps(
        focus_preview_data(financial_year_id),
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )
    return HttpResponse(response_json, content_type="application/json")


def focus_area_preview(request, financial_year_id, focus_slug):
    selected_financial_year = get_object_or_404(FinancialYear, slug=financial_year_id)
    context = {
        "focus_area_slug": focus_slug,
        "selected_financial_year": selected_financial_year.slug,
        "page": {"layout": "focus_page", "data_key": ""},
        "navbar": MainMenuItem.objects.prefetch_related("children").all(),
        "latest_year": FinancialYear.get_latest_year().slug,
    }
    return render(request, "focus_page.html", context)


def department_preview_json(
    request, financial_year_id, sphere_slug, government_slug, phase_slug
):
    response_json = json.dumps(
        get_preview_page(financial_year_id, phase_slug, government_slug, sphere_slug),
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )
    return HttpResponse(response_json, content_type="application/json")


def department_preview(
    request, financial_year_id, sphere_slug, government_slug, department_slug
):
    selected_financial_year = get_object_or_404(FinancialYear, slug=financial_year_id)
    context = {
        "department_slug": department_slug,
        "sphere_slug": sphere_slug,
        "government_slug": government_slug,
        "selected_financial_year": selected_financial_year.slug,
        "page": {"layout": "department_preview", "data_key": ""},
        "navbar": MainMenuItem.objects.prefetch_related("children").all(),
        "latest_year": FinancialYear.get_latest_year().slug,
        "debug": settings.DEBUG,
    }
    return render(request, "department_preview.html", context)


def iym_datasets_json(request):
    department_name = request.GET.get("department_name", "")
    financial_year_id = request.GET.get("selected_year", "")

    get_object_or_404(FinancialYear, slug=financial_year_id)
    years = FinancialYear.get_available_years()

    return_obj = {}

    for year in years:
        department_obj = Department.objects.filter(
            name=department_name,
            government__sphere__slug="national",
            government__sphere__financial_year__slug=year.slug,
        ).first()
        comparison_obj = InYearSpending(department_obj)
        url = comparison_obj.get_aggregate_url()
        return_obj[year.slug] = {"url": url}

    response_json = json.dumps(
        return_obj,
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )
    return HttpResponse(response_json, content_type="application/json")


def robots(request):
    if settings.ROBOTS_DENY_ALL:
        text = "User-agent: *\nDisallow: /"
    else:
        text = "Sitemap: %s" % request.build_absolute_uri("/sitemap.xml")

    response = HttpResponse(text, content_type="text/plain")
    return response


def read_object_from_yaml(path_file):
    with open(path_file, "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def budget_summary_view(request):
    latest_provincial_year = (
        FinancialYear.objects.filter(spheres__slug="provincial")
        .annotate(num_depts=Count("spheres__governments__departments"))
        .filter(num_depts__gt=0)
        .first()
    )
    context = {
        "navbar": MainMenuItem.objects.prefetch_related("children").all(),
        "latest_year": FinancialYear.get_latest_year().slug,
        "latest_provincial_year": latest_provincial_year
        and latest_provincial_year.slug,
    }
    return render(request, "budget-summary.html", context)
