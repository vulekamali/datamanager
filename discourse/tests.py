# -*- coding: utf-8 -*-


from django.test import TestCase


class SSOTestCase(TestCase):
    fixtures = ["development-first-user"]

    def setUp(self):
        self.client.login(username="admin@localhost", password="password")

    def test_valid_request(self):
        """
        Test with example at
        https://meta.discourse.org/t/official-single-sign-on-for-discourse-sso/13045
        """
        with self.settings(
            DISCOURSE_SSO_SECRET="d836444a9e4084d5b224a60c208dce14",
            DISCOURSE_SSO_URLS={
                "somessoclient": {
                    "DISCOURSE_SSO_SECRET": "http://www.example.com/discourse/sso"
                }
            },
        ):
            params = {
                "sso": "bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI=\n",
                "sig": "2828aa29899722b35a2f191d34ef9b3ce695e0e6eeec47deb46d588d70c7cb56",
            }
            response = self.client.get("/somessoclient/sso", params)
            redirect_url = (
                "http://www.example.com/discourse/sso?"
                "sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&"
                "sig=2828aa29899722b35a2f191d34ef9b3ce695e0e6eeec47deb46d588d70c7cb56"
            )
            print(response.content)
            self.assertRedirects(
                response, redirect_url, status_code=302, fetch_redirect_response=False
            )
