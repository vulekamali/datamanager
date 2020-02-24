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
        EXCEPT response payload and thus signature are different because of different user data.
        """
        with self.settings(
            DISCOURSE_SSO_SECRET="d836444a9e4084d5b224a60c208dce14",
            DISCOURSE_SSO_URLS={
                "somessoclient": "http://discuss.example.com/session/sso_login"
            },
        ):
            params = {
                "sso": "bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI=\n",
                "sig": "2828aa29899722b35a2f191d34ef9b3ce695e0e6eeec47deb46d588d70c7cb56",
            }
            response = self.client.get("/somessoclient/sso", params)
            redirect_url = (
                "http://discuss.example.com/session/sso_login?"
                "sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGImZW1haWw9YWRtaW4lNDBsb2Nh%0AbGhvc3QmZXh0ZXJuYWxfaWQ9MSZ1c2VybmFtZT1hZG1pbiU0MGxvY2FsaG9zdCZuYW1lPQ%3D%3D%0A&"
                "sig=314288361dd37ffd54f61b620a5be30607fe05836318611a8d448d7c18375554"
            )
            self.assertRedirects(
                response, redirect_url, status_code=302, fetch_redirect_response=False
            )
