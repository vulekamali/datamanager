from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Indicator
from .filters import IndicatorFilter


class IndicatorSerializer(ModelSerializer):        
    class Meta:
        model = Indicator
        filterset_class = IndicatorFilter
        fields = '__all__'
        extra_fields = ['department_name', 'financial_year','government_name', 'sphere_name','frequency']

        def get_field_names(self, declared_fields, info):
            expanded_fields = super(IndicatorSerializer, self).get_field_names(declared_fields, info)

            if getattr(self.Meta, 'extra_fields', None):
                return expanded_fields + self.Meta.extra_fields
            else:
                return expanded_fields

    