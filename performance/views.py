from django.shortcuts import render
from .models import Indicator
from .serializer import IndicatorSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from django_filters import rest_framework as filters


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

class IndicatorReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IndicatorSerializer
    filterset_class = IndicatorFilter
    queryset = Indicator.objects.all()
    http_method_names = ['get','head']




    
    


