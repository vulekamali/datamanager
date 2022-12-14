#from django.test import TestCase
import json
from django.urls import reverse
from rest_framework.test import APITestCase,APIRequestFactory
from rest_framework import status
from .views import IndicatorViewSet
from performance.serializer import IndicatorSerializer
from performance.models import Indicator
# Create your tests here.


class indicator_API_Test(APITestCase):
    list_url = reverse("indicator-list")
    
    def test_api(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_200(self):
        fixture = ['test_api.json']
        result = list(fixture[0].items())
        self.response = self.client.post('api/v1/eqprs/indicator', result)
        self.assertEqual(self.response.status_code, "200")    


        