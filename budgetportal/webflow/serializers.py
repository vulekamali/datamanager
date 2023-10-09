from budgetportal.models import InfraProjectSnapshot
from drf_haystack.serializers import HaystackFacetSerializer, HaystackSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from ..search_indexes import InfraProjectIndex


class InfraProjectSnapshotSerializer(ModelSerializer):
    url_path = SerializerMethodField()

    def get_url_path(self, project):
        return project.get_absolute_url()

    class Meta:
        model = InfraProjectSnapshot
        fields = (
            "project_number",
            "name",
            "sphere",
            "government_label",
            "financial_year",
            "province",
            "department",
            "sector",
            "local_municipality",
            "district_municipality",
            "latitude",
            "longitude",
            "status",
            "start_date",
            "estimated_construction_start_date",
            "estimated_completion_date",
            "contracted_construction_end_date",
            "estimated_construction_end_date",
            "total_professional_fees",
            "total_construction_costs",
            "variation_orders",
            "estimated_total_project_cost",
            "expenditure_from_previous_years_professional_fees",
            "expenditure_from_previous_years_construction_costs",
            "expenditure_from_previous_years_total",
            "main_appropriation_professional_fees",
            "adjusted_appropriation_professional_fees",
            "main_appropriation_construction_costs",
            "adjusted_appropriation_construction_costs",
            "main_appropriation_total",
            "adjusted_appropriation_total",
            "actual_expenditure_q1",
            "actual_expenditure_q2",
            "actual_expenditure_q3",
            "actual_expenditure_q4",
            "budget_programme",
            "primary_funding_source",
            "nature_of_investment",
            "funding_status",
            "program_implementing_agent",
            "principle_agent",
            "main_contractor",
            "other_parties",
            "url_path",
        )


class InfaProjectCSVSnapshotSerializer(serializers.ModelSerializer):
    irm_snapshot = serializers.SerializerMethodField()

    class Meta:
        model = InfraProjectSnapshot
        exclude = [
            "created_at",
            "updated_at",
            "id",
            "project",
            "estimated_total_project_cost",
            "project_expenditure_total",
        ]

    def get_irm_snapshot(self, obj):
        return str(obj.irm_snapshot) if obj.irm_snapshot else ""


class InfraProjectCSVSerializer(HaystackSerializer):
    class Meta:
        index_classes = [InfraProjectIndex]
        fields = [
            "name",
            "irm_snapshot",
            "sphere",
            "government_label",
            "financial_year",
            "province",
            "department",
            "sector",
            "status",
            "status_order",
            "primary_funding_source",
            "estimated_completion_date",
            "estimated_total_project_cost",
            "url_path",
            "latitude",
            "longitude",
            "project_number",
            "local_municipality",
            "district_municipality",
            "budget_programme",
            "nature_of_investment",
            "funding_status",
            "program_implementing_agent",
            "principle_agent",
            "main_contractor",
            "other_parties",
            "start_date",
            "estimated_construction_start_date",
            "contracted_construction_end_date",
            "estimated_construction_end_date",
            "total_professional_fees",
            "total_construction_costs",
            "variation_orders",
            "expenditure_from_previous_years_professional_fees",
            "expenditure_from_previous_years_construction_costs",
            "expenditure_from_previous_years_total",
            "main_appropriation_professional_fees",
            "adjusted_appropriation_professional_fees",
            "main_appropriation_construction_costs",
            "adjusted_appropriation_construction_costs",
            "main_appropriation_total",
            "adjusted_appropriation_total",
            "actual_expenditure_q1",
            "actual_expenditure_q2",
            "actual_expenditure_q3",
            "actual_expenditure_q4",
        ]


class InfraProjectSerializer(HaystackSerializer):
    class Meta:
        # The `index_classes` attribute is a list of which search indexes
        # we want to include in the search.
        index_classes = [InfraProjectIndex]

        # The `fields` contains all the fields we want to include.
        # NOTE: Make sure you don't confuse these with model attributes. These
        # fields belong to the search index!
        fields = [
            "name",
            "sphere",
            "government_label",
            "province",
            "department",
            "sector",
            "status",
            "status_order",
            "primary_funding_source",
            "estimated_completion_date",
            "estimated_total_project_cost",
            "url_path",
            "latitude",
            "longitude",
            "financial_year",
        ]

    def __init__(self, *args, **kwargs):
        # https://www.django-rest-framework.org/api-guide/serializers/#example
        # Instantiate the superclass normally
        super(InfraProjectSerializer, self).__init__(*args, **kwargs)

        fields = self.context["request"].query_params.get("fields")
        if fields:
            fields = fields.split(",")
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class InfraProjectFacetSerializer(HaystackFacetSerializer):
    serialize_objects = True  # Setting this to True will serialize the

    # queryset into an `objects` list. This
    # is useful if you need to display the faceted
    # results. Defaults to False.

    class Meta:
        index_classes = [InfraProjectIndex]
        fields = [
            "sector",
            "government_label",
            "province",
            "department",
            "status",
            "primary_funding_source",
            "financial_year",
        ]
        field_options = {
            "sector": {},
            "government_label": {},
            "province": {},
            "department": {},
            "status": {},
            "primary_funding_source": {},
            "financial_year":{},
        }
