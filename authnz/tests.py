from django.test import TestCase
from django.conf import settings
import json
from newt.tests import MyTestClient, newt_base_url, login


class AuthTests(TestCase):
    fixtures = ["test_fixture.json"]

    def setUp(self):
        self.client = MyTestClient()

    def test_login(self):
        # Should not be logged in
        r = self.client.get(newt_base_url + "/auth")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['auth'], False)
        
        # Should be logged in
        r = self.client.post(newt_base_url + "/auth", data=login)
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['auth'], True)
        self.assertEquals(json_response['output']['username'], login['username'])

        # Loggen in self.client should return user info
        r = self.client.get(newt_base_url + "/auth")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['auth'], True)
        self.assertEquals(json_response['output']['username'], login['username'])


    def test_logout(self):
        # Should be logged in
        r = self.client.post(newt_base_url + "/auth", data=login)
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['auth'], True)
        self.assertEquals(json_response['output']['username'], login['username'])

        r = self.client.delete(newt_base_url + "/auth")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['auth'], False)

        r = self.client.get(newt_base_url + "/auth")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['auth'], False)
