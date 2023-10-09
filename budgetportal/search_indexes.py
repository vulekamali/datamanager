from budgetportal.infra_projects import status_order
from budgetportal.models import InfraProject
from django.db.models import Count
from haystack import indexes


class InfraProjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField()
    province = indexes.CharField(faceted=True)
    government_label = indexes.CharField(faceted=True)
    financial_year = indexes.CharField(faceted=True)
    sphere = indexes.CharField(faceted=True)
    department = indexes.CharField(faceted=True)
    sector = indexes.CharField(faceted=True)
    status = indexes.CharField(faceted=True)
    status_order = indexes.IntegerField()
    primary_funding_source = indexes.CharField(faceted=True)
    estimated_completion_date = indexes.DateField()
    estimated_total_project_cost = indexes.FloatField()
    latitude = indexes.CharField()
    longitude = indexes.CharField()
    url_path = indexes.CharField()

    irm_snapshot = indexes.CharField(indexed=False)
    project_number = indexes.CharField(indexed=False)
    local_municipality = indexes.CharField(indexed=False)
    district_municipality = indexes.CharField(indexed=False)
    budget_programme = indexes.CharField(indexed=False)
    nature_of_investment = indexes.CharField(indexed=False)
    funding_status = indexes.CharField(indexed=False)
    program_implementing_agent = indexes.CharField(indexed=False)
    principle_agent = indexes.CharField(indexed=False)
    main_contractor = indexes.CharField(indexed=False)
    other_parties = indexes.CharField(indexed=False)
    start_date = indexes.DateField(indexed=False)
    estimated_construction_start_date = indexes.DateField(indexed=False)
    contracted_construction_end_date = indexes.DateField(indexed=False)
    estimated_construction_end_date = indexes.DateField(indexed=False)

    total_professional_fees = indexes.FloatField(indexed=False)
    total_construction_costs = indexes.FloatField(indexed=False)
    variation_orders = indexes.FloatField(indexed=False)
    expenditure_from_previous_years_professional_fees = indexes.FloatField(
        indexed=False
    )
    expenditure_from_previous_years_construction_costs = indexes.FloatField(
        indexed=False
    )
    expenditure_from_previous_years_total = indexes.FloatField(indexed=False)
    main_appropriation_professional_fees = indexes.FloatField(indexed=False)
    adjusted_appropriation_professional_fees = indexes.FloatField(indexed=False)
    main_appropriation_construction_costs = indexes.FloatField(indexed=False)
    adjusted_appropriation_construction_costs = indexes.FloatField(indexed=False)
    main_appropriation_total = indexes.FloatField(indexed=False)
    adjusted_appropriation_total = indexes.FloatField(indexed=False)
    actual_expenditure_q1 = indexes.FloatField(indexed=False)
    actual_expenditure_q2 = indexes.FloatField(indexed=False)
    actual_expenditure_q3 = indexes.FloatField(indexed=False)
    actual_expenditure_q4 = indexes.FloatField(indexed=False)

    def get_model(self):
        return InfraProject

    def prepare_name(sef, object):
        return object.project_snapshots.latest().name

    def prepare_status(sef, object):
        return object.project_snapshots.latest().status

    def prepare_status_order(self, object):
        return status_order.get(object.project_snapshots.latest().status, 100)

    def prepare_government_label(sef, object):
        return object.project_snapshots.latest().government_label

    def prepare_province(sef, object):
        return object.project_snapshots.latest().province

    def prepare_sphere(sef, object):
        return object.project_snapshots.latest().irm_snapshot.sphere.slug

    def prepare_financial_year(sef, object):
        return object.project_snapshots.latest().government_label

    def prepare_department(sef, object):
        return object.project_snapshots.latest().department

    def prepare_sector(sef, object):
        return object.project_snapshots.latest().sector

    def prepare_primary_funding_source(sef, object):
        return object.project_snapshots.latest().primary_funding_source

    def prepare_estimated_total_project_cost(sef, object):
        return object.project_snapshots.latest().estimated_total_project_cost

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

    def prepare_irm_snapshot(self, object):
        return str(object.project_snapshots.latest().irm_snapshot)

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
        return (
            object.project_snapshots.latest().expenditure_from_previous_years_professional_fees
        )

    def prepare_expenditure_from_previous_years_construction_costs(sef, object):
        return (
            object.project_snapshots.latest().expenditure_from_previous_years_construction_costs
        )

    def prepare_expenditure_from_previous_years_total(sef, object):
        return object.project_snapshots.latest().expenditure_from_previous_years_total

    def prepare_project_expenditure_total(sef, object):
        return object.project_snapshots.latest().project_expenditure_total

    def prepare_main_appropriation_professional_fees(sef, object):
        return object.project_snapshots.latest().main_appropriation_professional_fees

    def prepare_adjusted_appropriation_professional_fees(sef, object):
        return (
            object.project_snapshots.latest().adjusted_appropriation_professional_fees
        )

    def prepare_adjusted_appropriation_construction_costs(sef, object):
        return (
            object.project_snapshots.latest().adjusted_appropriation_construction_costs
        )

    def prepare_main_appropriation_total(sef, object):
        return object.project_snapshots.latest().main_appropriation_total

    def prepare_adjusted_appropriation_total(sef, object):
        return object.project_snapshots.latest().adjusted_appropriation_total

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
        return InfraProject.objects.annotate(
            project_snapshots_count=Count("project_snapshots")
        ).filter(project_snapshots_count__gte=1)
