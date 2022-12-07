from rest_framework import serializers
from .models import *


class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicatorValue
        fields = "__all__"