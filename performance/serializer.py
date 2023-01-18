from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Indicator


class IndicatorSerializer(ModelSerializer):
    department_name = serializers.SerializerMethodField('get_department_name')
    financial_year = serializers.SerializerMethodField('get_financialYear')
    government_name = serializers.SerializerMethodField('get_government_name')
    sphere_name = serializers.SerializerMethodField('get_sphere_name')
    frequency = serializers.SerializerMethodField('get_frequency')

    def get_department_name(self, indicator):
        department_name = indicator.budgetportal.models.government.Department.department_name
        return department_name

    def get_financialYear(self, indicator):
        financial_year = indicator.budgetportal.models.government.Department.financial_year
        return financial_year  

    def get_government_name(self, indicator):
        government_name = indicator.budgetportal.models.government.Department.government_name
        return government_name

    def get_sphere_name(self, indicator):
        sphere_name = indicator.department.government.sphere.slug
        return sphere_name
        
    def get_frequency(self, indicator):
        frequency = indicator.department.frequency
        return frequency 
        
    class Meta:
        model = Indicator
        fields = '__all__'
        extra_fields = ['department_name', 'financial_year','government_name', 'sphere_name','frequency']

    def get_field_names(self, declared_fields, info):
        expanded_fields = super(IndicatorSerializer, self).get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields
        else:
            return expanded_fields

    