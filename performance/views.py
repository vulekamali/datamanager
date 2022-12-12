from django.shortcuts import render
from .models import Indicator
from .serializer import IndicatorSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet

# Create your views here.

class IndicatorViewSet(ReadOnlyModelViewSet):
    serializer_class=IndicatorSerializer
    queryset = Indicator.objects.all()
    


