from django.shortcuts import render
from .models import Indicator
from .serializer import IndicatorSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets

# Create your views here.

class IndicatorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IndicatorSerializer
    queryset = Indicator.objects.all()
    


