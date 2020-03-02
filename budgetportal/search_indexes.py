from budgetportal.models import ProvInfraProject
from django.db.models import Count
from haystack import indexes
from .prov_infra_projects import status_order


class ProvInfraProjectIndex(indexes.SearchIndex, indexes.Indexable):
    id = indexes.IntegerField()
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField()
    province = indexes.CharField(faceted=True)
    department = indexes.CharField(faceted=True)
    status = indexes.CharField(faceted=True)
    status_order = indexes.IntegerField()
    primary_funding_source = indexes.CharField(faceted=True)
    estimated_completion_date = indexes.DateField()
    total_project_cost = indexes.FloatField()
    latitude = indexes.CharField()
    longitude = indexes.CharField()
    url_path = indexes.CharField()

    project_number = indexes.CharField()
    local_municipality = indexes.CharField()
    district_municipality = indexes.CharField()
    budget_programme = indexes.CharField()
    nature_of_investment = indexes.CharField()
    funding_status = indexes.CharField()
    program_implementing_agent = indexes.CharField()
    principle_agent = indexes.CharField()
    main_contractor = indexes.CharField()
    other_parties = indexes.CharField()
    start_date = indexes.DateField()
    estimated_construction_start_date = indexes.DateField()
    contracted_construction_end_date = indexes.DateField()
    estimated_construction_end_date = indexes.DateField()

    total_professional_fees = indexes.DecimalField()
    total_construction_costs = indexes.DecimalField()
    variation_orders = indexes.DecimalField()
    expenditure_from_previous_years_professional_fees = indexes.DecimalField()
    expenditure_from_previous_years_construction_costs = indexes.DecimalField()
    expenditure_from_previous_years_total = indexes.DecimalField()
    project_expenditure_total = indexes.DecimalField()
    main_appropriation_professional_fees = indexes.DecimalField()
    adjustment_appropriation_professional_fees = indexes.DecimalField()
    main_appropriation_construction_costs = indexes.DecimalField()
    adjustment_appropriation_construction_costs = indexes.DecimalField()
    main_appropriation_total = indexes.DecimalField()
    adjustment_appropriation_total = indexes.DecimalField()
    actual_expenditure_q1 = indexes.DecimalField()
    actual_expenditure_q2 = indexes.DecimalField()
    actual_expenditure_q3 = indexes.DecimalField()
    actual_expenditure_q4 = indexes.DecimalField()

    def get_model(self):
        return ProvInfraProject

    def prepare_id(self, object):
        return object.project_snapshots.latest().id

    def prepare_name(sef, object):
        return object.project_snapshots.latest().name

    def prepare_status(sef, object):
        return object.project_snapshots.latest().status

    def prepare_status_order(self, object):
        return status_order.get(object.project_snapshots.latest().status, 100)

    def prepare_province(sef, object):
        return object.project_snapshots.latest().province

    def prepare_department(sef, object):
        return object.project_snapshots.latest().department

    def prepare_primary_funding_source(sef, object):
        return object.project_snapshots.latest().primary_funding_source

    def prepare_total_project_cost(sef, object):
        return object.project_snapshots.latest().total_project_cost

    def prepare_estimated_completion_date(sef, object):
        date = object.project_snapshots.latest().estimated_completion_date
        if date:
            return date.isoformat()

    def prepare_latitude(sef, object):
        return object.project_snapshots.latest().latitude

    def prepare_longitude(sef, object):
        return object.project_snapshots.latest().longitude

    def prepare_url_path(sef, object):
        return object.get_absolute_url()

    def prepare_project_number(sef, object):
        return object.project_snapshots.latest().project_number

    def prepare_local_municipality(sef, object):
        return object.project_snapshots.latest().local_municipality

    def prepare_district_municipality(sef, object):
        return object.project_snapshots.latest().district_municipality

    def prepare_budget_programme(sef, object):
        return object.project_snapshots.latest().budget_programme

    def prepare_nature_of_investment(sef, object):
        return object.project_snapshots.latest().nature_of_investment

    def prepare_funding_status(sef, object):
        return object.project_snapshots.latest().funding_status

    def prepare_program_implementing_agent(sef, object):
        return object.project_snapshots.latest().program_implementing_agent

    def prepare_principle_agent(sef, object):
        return object.project_snapshots.latest().principle_agent

    def prepare_main_contractor(sef, object):
        return object.project_snapshots.latest().main_contractor

    def prepare_other_parties(sef, object):
        return object.project_snapshots.latest().other_parties

    def prepare_start_date(sef, object):
        return object.project_snapshots.latest().start_date

    def prepare_estimated_construction_start_date(sef, object):
        return object.project_snapshots.latest().estimated_construction_start_date

    def prepare_contracted_construction_end_date(sef, object):
        return object.project_snapshots.latest().contracted_construction_end_date

    def prepare_estimated_construction_end_date(sef, object):
        return object.project_snapshots.latest().estimated_construction_end_date

    def prepare_total_professional_fees(sef, object):
        return object.project_snapshots.latest().total_professional_fees

    def prepare_total_construction_costs(sef, object):
        return object.project_snapshots.latest().total_construction_costs

    def prepare_variation_orders(sef, object):
        return object.project_snapshots.latest().variation_orders

    def prepare_expenditure_from_previous_years_professional_fees(sef, object):
        return object.project_snapshots.latest().expenditure_from_previous_years_professional_fees

    def prepare_expenditure_from_previous_years_construction_costs(sef, object):
        return object.project_snapshots.latest().expenditure_from_previous_years_construction_costs

    def prepare_expenditure_from_previous_years_total(sef, object):
        return object.project_snapshots.latest().expenditure_from_previous_years_total

    def prepare_project_expenditure_total(sef, object):
        return object.project_snapshots.latest().project_expenditure_total

    def prepare_main_appropriation_professional_fees(sef, object):
        return object.project_snapshots.latest().main_appropriation_professional_fees

    def prepare_adjustment_appropriation_professional_fees(sef, object):
        return object.project_snapshots.latest().adjustment_appropriation_professional_fees

    def prepare_adjustment_appropriation_construction_costs(sef, object):
        return object.project_snapshots.latest().adjustment_appropriation_construction_costs

    def prepare_main_appropriation_total(sef, object):
        return object.project_snapshots.latest().main_appropriation_total

    def prepare_adjustment_appropriation_total(sef, object):
        return object.project_snapshots.latest().adjustment_appropriation_total

    def prepare_actual_expenditure_q1(sef, object):
        return object.project_snapshots.latest().actual_expenditure_q1

    def prepare_actual_expenditure_q2(sef, object):
        return object.project_snapshots.latest().actual_expenditure_q2

    def prepare_actual_expenditure_q3(sef, object):
        return object.project_snapshots.latest().actual_expenditure_q3

    def prepare_actual_expenditure_q4(sef, object):
        return object.project_snapshots.latest().actual_expenditure_q4

    def should_update(self, instance, **kwargs):
        return instance.project_snapshots.count()

    def index_queryset(self, using=None):
        return ProvInfraProject.objects.annotate(
            project_snapshots_count=Count("project_snapshots")
        ).filter(project_snapshots_count__gte=1)
