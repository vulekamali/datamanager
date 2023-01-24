import django_filters
from .models import Indicator

class IndicatorFilter(django_filters.FilterSet):
    class Meta:
        model = Indicator
        filter_fields = {'department_name':['exact'],
                            'financial_year':['exact'],
                            'government_name': ['exact'],
                            'sphere_name': ['exact'],
                            'frequency':['exact'],
                            'mtsf_outcome':['exact'],
                            'sector':['exact']}