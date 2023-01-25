from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Indicator
from .filters import IndicatorFilter


class IndicatorSerializer(ModelSerializer):
    department_name = serializers.SerializerMethodField('_get_department_name')
    financial_year = serializers.SerializerMethodField('_get_financialYear')
    government_name = serializers.SerializerMethodField('_get_government_name')
    sphere_name = serializers.SerializerMethodField('_get_sphere_name')
    frequency = serializers.SerializerMethodField('_get_frequency')


    def _get_department_name(self, dep_obj):
        department_name = dep_obj.budgetportal.models.government.department.department_name
        return department_name

    def _get_financialYear(self, fy_obj):
        financial_year = fy_obj.budgetportal.models.government.department.financial_year
        return financial_year  

    def _get_government_name(self, gov_obj):
        government_name = gov_obj.budgetportal.models.government.department.government_name
        return government_name

    def _get_sphere_name(self, sphere_obj):
        sphere_name = sphere_obj.budgetportal.government.department.sphere
        return sphere_name
            
    def _get_frequency(self, freq_obj):
        frequency = freq_obj.department.frequency
        return frequency    

    class Meta:
        model = Indicator
        filterset_class = IndicatorFilter
        model_fields = ['__all__']
        extra_fields = ['department_name', 'financial_year','government_name', 'sphere_name','frequency']
        fields = model_fields + extra_fields
   