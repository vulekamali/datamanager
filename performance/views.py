from django.shortcuts import render
from .models import Indicator
from .serializer import IndicatorSerializer
from rest_framework import generics

class IndicatorListView(generics.ListAPIView):
    serializer_class = IndicatorSerializer
    queryset = Indicator.objects.all()
