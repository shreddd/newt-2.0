from django.test import TestCase
from django.conf import settings
import json
import os
import random, string
from newt.tests import MyTestClient, newt_base_url, login
try:
    from newt.local_settings import test_machine as machine
except ImportError:
    machine = "localhost"


class FileTests(TestCase):
    def setUp(self):
        self.client = MyTestClient()
        self.client.post(newt_base_url + "/auth", data=login)

    def test_root(self):
        r = self.client.get(newt_base_url+'/file')
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['status'], "OK")
        self.assertIn(machine, json_response['output'])
        
    def test_getdir(self):        
        r = self.client.get(newt_base_url+'/file/'+machine+"/")
        self.assertEquals(r.status_code, 200)

        json_response = r.json()
        self.assertEquals(json_response['status'], "OK")
        
        self.assertTrue(len(json_response['output']) >= 2)
        self.assertEquals(json_response['output'][0]['name'], ".")
        self.assertEquals(json_response['output'][1]['name'], "..")
        
    def test_getfile(self):
        # TODO: Use namedtmpfile instead
        tmpfile = "/tmp/tmp_newt.txt"
        with open(tmpfile, 'w') as f:
            f.write('hello newt')
        # f.flush()
        f.close()
        r = self.client.get(newt_base_url+'/file/'+machine+'/tmp/tmp_newt.txt?download=true')
        self.assertEquals(r.status_code, 200)

        self.assertEquals(r.streaming_content.next(), 'hello newt')
        os.remove(tmpfile)

    def test_uploadfile(self):
        rand_string = ''.join(random.choice(string.ascii_letters) for _ in xrange(10))
        r = self.client.put(newt_base_url + "/file/"+machine+"/tmp/tmp_newt_2.txt", data=rand_string)
        self.assertEqual(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['location'], "/tmp/tmp_newt_2.txt")
        r = self.client.get(newt_base_url+'/file/'+machine+'/tmp/tmp_newt_2.txt?download=true')
        self.assertEquals(r.status_code, 200)
        self.assertEquals(r.streaming_content.next(), rand_string)
        try:
            os.remove("/tmp/tmp_newt_2.txt")
        except Exception:
            pass
