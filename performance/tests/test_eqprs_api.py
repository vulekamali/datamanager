import json
from django.urls import reverse
from rest_framework.test import APITestCase,APIRequestFactory
from rest_framework import status
from performance.views import IndicatorReadOnlyModelViewSet
from performance.serializer import IndicatorSerializer
from performance.models import Indicator
import json
import pprint

class indicator_API_Test(APITestCase):
    list_url = '/performance/api/v1/eqprs/'
    fixture = ['test_api.json']

    def test_api(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.load(open("performance/test_api.json"))
        response_data=json.dumps(data)
        dict_json=json.loads(response_data)

        found = False
        message1 ="1.2.1 Percentage of valid invoices paid with in 30 days upon receipt by the department"
        message2 = "1.1.1 Unqualified audit opinion"
        testvalue= ""
        for data1 in dict_json:
            for key, value in data1.items():
                if key == "fields":
                    for key2, value2 in value.items():
                        # print(kk)
                        if key2 == "indicator_name":
                            print(value2)
                            testvalue = value2

                            if message1 == testvalue or message2== testvalue:
                                found = True

        self.assertTrue(found, True)

    def create(self):
        response = self.client.post(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self):
        response = self.client.patch(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
