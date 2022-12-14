from rest_framework.serializers import ModelSerializer
from rest_framework import permissions
from .models import Indicator


class IndicatorSerializer(ModelSerializer):
    class Meta:
        model = Indicator
        fields = '__all__'
    