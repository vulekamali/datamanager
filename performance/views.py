from django.shortcuts import render
from .models import Indicator
from .serializer import IndicatorSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from django_filters import rest_framework as filters
from .filters import IndicatorFilter

<<<<<<< Updated upstream
<<<<<<< HEAD

class IndicatorFilter(filters.FilterSet):
    model = Indicator
    financial_year = filters.CharFilter(lookup_expr= 'icontains')
    government_name = filters.CharFilter(lookup_expr= 'icontains')
    sphere_name = filters.CharFilter(lookup_expr= 'icontains')
    frequency = filters.CharFilter(lookup_expr= 'icontains')
    mtsf_outcome = filters.CharFilter(lookup_expr= 'icontans')
    sector = filters.CharFilter(lookup_expr= 'icontans')

    class Meta:
        model = Indicator
        filter_fields = ('department_name','financial_year', 'government_name','sphere_name','frequency', 'mtsf_outcome','sector')
=======
                         
>>>>>>> Stashed changes

=======
>>>>>>> eqprs-api
class IndicatorReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IndicatorSerializer
    filterset_class = IndicatorFilter
    queryset = Indicator.objects.all()
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
    indicatorfilter = IndicatorFilter
>>>>>>> Stashed changes
    indicatorfilter = IndicatorFilter
>>>>>>> Stashed changes
    http_method_names = ['get','head']




    
    


=======
    http_method_names = ['get','head']
>>>>>>> eqprs-api
