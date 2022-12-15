from django.shortcuts import render
from .models import Indicator
from .serializer import IndicatorSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets

# Create your views here.

class IndicatorReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IndicatorSerializer
    queryset = Indicator.objects.all()
    http_method_names = ['get', 'put', 'head']
    


