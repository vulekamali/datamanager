from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.test import Client


class indicator_API_Test(APITestCase):
    list_url = "/performance/api/v1/eqprs/"
    fixtures = ["test_api.json"]

    def test_api(self):

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        response_payload = self.client.get(self.list_url).json()

        found = False
        message1 = "1.2.1 Percentage of valid invoices paid within 30 days upon receipt by the department"
        message2 = "1.1.1 Unqualified audit opinion"
        if (
            response_payload["results"]["items"][0]["indicator_name"] == message2
            or response_payload["results"]["items"][1]["indicator_name"] == message1
        ):
            found = True

        self.assertEqual(found, True)
        self.assertTrue(found, True)

    def test_create(self):
        response = self.client.post(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update(self):
        response = self.client.patch(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_text_search(self):
        filter_url = self.list_url + "?page=1&q=Unqualified%20audit%20opinion"
        response_payload = self.client.get(filter_url).json()
        self.assertEqual(len(response_payload["results"]["items"]), 1)

    def test_frequency_search(self):
        filter_url = self.list_url + "?page=1&frequency=Annually"
        response_payload = self.client.get(filter_url).json()
        self.assertEqual(len(response_payload["results"]["items"]), 1)
