from rest_framework.serializers import ModelSerializer, SerializerMethodField

from budgetportal.models import ProvInfraProject


class ProvInfraProjectSerializer(ModelSerializer):
    url = SerializerMethodField("url_path")

    def url_path(self, project):
        return project.get_url_path(project)

    class Meta:
        model = ProvInfraProject
        fields = (
            "project_number",
            "name",
            "province",
            "department",
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
            "total_project_cost",
            "expenditure_from_previous_years_professional_fees",
            "expenditure_from_previous_years_construction_costs",
            "expenditure_from_previous_years_total",
            "project_expenditure_total",
            "main_appropriation_professional_fees",
            "adjustment_appropriation_professional_fees",
            "main_appropriation_construction_costs",
            "adjustment_appropriation_construction_costs",
            "main_appropriation_total",
            "adjustment_appropriation_total",
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
            "url",
        )
