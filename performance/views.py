from django.shortcuts import render
from models import *
from serializer import *
from rest_framework import viewsets
from rest_framework.response import Response

# Create your views here.
# This viewset automatically provides `list` and `retrieve` actions.
class IndicatorViewSet(viewsets.ModelViewSet):
    queryset = IndicatorValue.objects.all()
#    serializer_class=IndicatorSerializer

    def list(self, request):
        serializer_class = IndicatorSerializer(self.queryset, many =True)
        return Response(serializer_class.data)

