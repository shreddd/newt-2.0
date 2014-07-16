from django.test import TestCase
from django.conf import settings
import json
from newt.tests import MyTestClient, newt_base_url, login


class StatusTests(TestCase):
    def setUp(self):
        self.client = MyTestClient()

    def test_all(self):
        r = self.client.get(newt_base_url+'/status')
        self.assertEquals(r.status_code, 200)

        json_response = r.json()
        self.assertEquals(json_response['status'], "OK")

        for x in json_response['output']:
            if x['system'] == "localhost":
                self.assertEquals(x['status'], 'up')
            else:
                self.assertIn(x['status'], ['up', 'down'])

    def test_one(self):
        system = settings.NEWT_CONFIG['SYSTEMS'][0]['NAME']
        r = self.client.get('%s/status/%s' % (newt_base_url, system))
        self.assertEquals(r.status_code, 200)

        json_response = r.json()
        self.assertEquals(json_response['status'], "OK")

        self.assertEquals(json_response['output']['status'], 'up')