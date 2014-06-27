from django.test import TestCase
from django.conf import settings
import json
import os
from newt.tests import MyTestClient, newt_base_url, login


class FileTests(TestCase):
    def setUp(self):
        self.client = MyTestClient()

    def test_root(self):
        r = self.client.get(newt_base_url+'/file')
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['status'], "OK")
        self.assertIn('localhost', json_response['output'])
        
    def test_getdir(self):
        file_list = os.listdir("/")
        # Add . and .. to listdir results
        file_list = file_list + ['.', '..']
        file_list.sort()
        self.assertTrue(len(file_list)>0)
        
        r = self.client.get(newt_base_url+'/file/localhost/')
        self.assertEquals(r.status_code, 200)

        json_response = r.json()
        self.assertEquals(json_response['status'], "OK")
        
        self.assertEquals(len(json_response['output']), len(file_list))
        newt_file_list = [ str(line['name']) for line in json_response['output'] ]
        newt_file_list.sort()
        
        self.maxDiff = None
        self.assertEquals(newt_file_list, file_list)
        
    def test_getfile(self):
        # TODO: Use namedtmpfile instead
        tmpfile = "/tmp/tmp_newt.txt"
        with open(tmpfile, 'w') as f:
            f.write('hello newt')
        # f.flush()
        f.close()
        r = self.client.get(newt_base_url+'/file/localhost/tmp/tmp_newt.txt?download=true')
        self.assertEquals(r.status_code, 200)

        self.assertEquals(r.streaming_content.next(), 'hello newt')
        os.remove(tmpfile)

    def test_uploadfile(self):
        r = self.client.put(newt_base_url + "/file/localhost/tmp/tmp_newt_2.txt", data="hello newt")
        self.assertEqual(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['location'], "/tmp/tmp_newt_2.txt")
        r = self.client.get(newt_base_url+'/file/localhost/tmp/tmp_newt_2.txt?download=true')
        self.assertEquals(r.status_code, 200)
        self.assertEquals(r.streaming_content.next(), 'hello newt')
        os.remove("/tmp/tmp_newt_2.txt")
