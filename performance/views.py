from django.shortcuts import render
from .models import Indicator
from .serializer import IndicatorSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

# class IndicatorFilter(filters.FilterSet):

#     department_name = filters.CharFilter(lookup_expr= 'icontains')

#     class Meta:
#         model = Indicator
#         filter_fields = ['department_name']

class IndicatorReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IndicatorSerializer
   # filterset_class = IndicatorFilter
    queryset = Indicator.objects.all()
    http_method_names = ['get','head']
    filter_backends = (SearchFilter, OrderingFilter)
    search_field = ['department_name', 'financial_year','government_name', 'sphere_name','frequency']




    
    


