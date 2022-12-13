from django.shortcuts import render
from .models import Indicator
from .serializer import IndicatorSerializer
from rest_framework.viewsets import ModelViewSet

# Create your views here.

class IndicatorViewSet(ModelViewSet):
    serializer_class = IndicatorSerializer
    queryset = Indicator.objects.all()
    


