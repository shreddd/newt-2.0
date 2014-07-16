from django.test import TestCase
from django.conf import settings
from django.test.client import Client
import json

newt_base_url = "/api"
try:
    from local_settings import test_login as login
except ImportError:
    login = {"username": "nimonly", "password": "testpassword"}

class MyTestClient(Client):
    def request(self, **request):
        response = super(MyTestClient, self).request(**request)
        def get_headers(response):
            headers = {}
            temp = response.serialize_headers().splitlines()
            for key, val in map(lambda line: line.split(": "), temp):
                headers[key.lower()] = val
            return headers
        response.headers = get_headers(response)
        response.json = lambda: json.loads(response.content)
        response.status_code = int(response.status_code)
        return response

class BasicTests(TestCase):
    def setUp(self):
        self.client = MyTestClient()

    def test_root(self):
        """
        test basic root URI
        """
        r = self.client.get(newt_base_url)
        self.assertEquals(r.status_code, 200)

        json_response = r.json()
        self.assertEquals(json_response['status'], "OK")
        self.assertEquals(json_response['status_code'], 200)
        self.assertEquals(json_response['error'], "")
        self.assertTrue(json_response['output']['version'], settings.NEWT_VERSION)
        self.assertEquals(r.headers['content-type'], 'application/json')


    def test_error(self):
        r = self.client.post(newt_base_url)
        self.assertEquals(r.status_code, 501)

        json_response = r.json()
        self.assertEquals(json_response['status'], "ERROR")
        