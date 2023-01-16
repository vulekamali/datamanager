import json
from django.urls import reverse
from rest_framework.test import APITestCase,APIRequestFactory
from rest_framework import status
from performance.views import IndicatorReadOnlyModelViewSet
from performance.serializer import IndicatorSerializer
from performance.models import Indicator

class indicator_API_Test(APITestCase):
    list_url = '/performance/api/v1/eqprs'
    fixture = ['test_api.json']
    
    def test_api(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def create(self):
        response = self.client.post(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)    

    def update(self):
        response = self.client.patch(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)     



    




        