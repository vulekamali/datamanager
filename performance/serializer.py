from rest_framework.serializers import ModelSerializer
from .models import Indicator
from budgetportal.models.government import Department, Government, Sphere, FinancialYear


class FinancialYearSerializer(ModelSerializer):
    class Meta:
        model = FinancialYear
        fields = ("slug",)


class SphereSerializer(ModelSerializer):
    financial_year = FinancialYearSerializer()

    class Meta:
        model = Sphere
        fields = (
            "financial_year",
            "name",
        )


class GovernmentSerializer(ModelSerializer):
    sphere = SphereSerializer()

    class Meta:
        model = Government
        fields = (
            "sphere",
            "name",
        )


class DepartmentSerializer(ModelSerializer):
    government = GovernmentSerializer()

    class Meta:
        model = Department
        fields = (
            "government",
            "name",
        )


class IndicatorSerializer(ModelSerializer):
    department = DepartmentSerializer()

    class Meta:
        model = Indicator
        exclude = (
            "source",
            "content_search",
            "uid",
            "created_at",
            "id",
            "annual_otp_comments",
            "annual_national_comments",
            "annual_dpme_coordinator_comments",
            "annual_treasury_comments",
            "q1_national_comments",
            "q1_otp_comments",
            "q1_dpme_coordinator_comments",
            "q1_treasury_comments",
            "q2_national_comments",
            "q2_otp_comments",
            "q2_dpme_coordinator_comments",
            "q2_treasury_comments",
            "q3_national_comments",
            "q3_otp_comments",
            "q3_dpme_coordinator_comments",
            "q3_treasury_comments",
            "q4_national_comments",
            "q4_otp_comments",
            "q4_dpme_coordinator_comments",
            "q4_treasury_comments",
        )
