from django.test import TestCase
from django.conf import settings
import json
from newt.tests import MyTestClient, newt_base_url, login


class AcctTests(TestCase):
    fixtures = ["test_fixture.json"]

    def setUp(self):
        self.client = MyTestClient()

    def test_info_ret(self):
        self.client.post(newt_base_url + "/auth", data=login)

        r = self.client.get(newt_base_url + "/account/user/%s/" % login['username'])
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['username'], login['username'])

        r = self.client.get(newt_base_url + "/account/user/id/2/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['username'], login['username'])

        r = self.client.get(newt_base_url + "/account/group/id/1/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['name'], "Test Group")
