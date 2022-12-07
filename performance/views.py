from django.shortcuts import render
from models import *
from serializer import *
from rest_framework import viewsets

# Create your views here.
class IndicatorViewSet(viewsets.ModelViewSet):
    queryset = IndicatorValue.objects.all()
    serializer_class=IndicatorSerializer

