"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

from django.test import TestCase
from django.conf import settings
from django.test.client import Client
import socket
import os
import json

newt_base_url = "/api"

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
        # self.assertEquals(r.headers['content-type'], 'application/json')

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

class CommandTests(TestCase):
    def setUp(self):
        self.client = MyTestClient()

    def test_root(self):
        r = self.client.get(newt_base_url+'/command')
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['status'], "OK")
        self.assertIn('localhost', json_response['output'])

    def test_command(self):
        r = self.client.post(newt_base_url+'/command/localhost', {'command': '/bin/hostname'})
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['status'], "OK")

        hostname = socket.gethostname()
        self.assertEquals(hostname, json_response['output']['stdout'].strip())


    def test_command_with_args(self):
        # Run ls in / 
        r = self.client.post(newt_base_url+'/command/localhost', {'command': '/bin/ls -a /'})
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['status'], "OK")
        # os.listdir() leaves off . and .. so add them in
        files = ['.', '..'] + os.listdir('/')
        files.sort()
        newtfiles = json_response['output']['stdout'].strip().split('\n')
        newtfiles.sort()
        self.assertEquals(files, newtfiles)



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
            
        r = self.client.get(newt_base_url+'/file/localhost/tmp/tmp_newt.txt?download=true')
        self.assertEquals(r.status_code, 200)

        self.assertEquals(r.streaming_content.next(), 'hello newt')
        os.remove(tmpfile)

class AuthTests(TestCase):
    fixtures = ["test_fixture.json"]
    payload = { 'username': "testuser", 'password': "test1pass" }

    def setUp(self):
        self.client = MyTestClient()

    def test_login(self):
        # Should not be logged in
        r = self.client.get(newt_base_url + "/auth")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['auth'], False)
        
        # Should be logged in
        r = self.client.post(newt_base_url + "/auth", data=self.payload)
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['auth'], True)
        self.assertEquals(json_response['output']['username'], self.payload['username'])

        # Loggen in self.client should return user info
        r = self.client.get(newt_base_url + "/auth")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['auth'], True)
        self.assertEquals(json_response['output']['username'], self.payload['username'])


    def test_logout(self):
        # Should be logged in
        r = self.client.post(newt_base_url + "/auth", data=self.payload)
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['auth'], True)
        self.assertEquals(json_response['output']['username'], self.payload['username'])

        r = self.client.delete(newt_base_url + "/auth")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['auth'], False)

        r = self.client.get(newt_base_url + "/auth")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['auth'], False)

class StoresTests(TestCase):
    fixtures = ["test_fixture.json"]

    def setUp(self):
        self.client = MyTestClient()
        try:
            from pymongo import MongoClient
            db = MongoClient()['stores']
            db.test_store_1.drop()
            db.permissions.remove({"name":"test_store_1"})
        except Exception:
            pass
        # Assumes that the stores database is empty
    def test_stores_basic(self):
        r = self.client.get(newt_base_url + "/stores")
        self.assertEquals(r.status_code, 200)

    def test_stores_creation(self):
        # Creates a new store
        r = self.client.post(newt_base_url + "/stores")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        store_id = json_response['output']['id']
        
        # Ensures that new store is empty
        r = self.client.get(newt_base_url + "/stores/" + store_id + "/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output'], [])
        
        # Tests insertion
        payload = {"data": json.dumps({"foo":"bar"})}
        r = self.client.post(newt_base_url + "/stores/" + store_id + "/",
                          data=payload)

        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        obj_id = json_response['output']['id']
        # Checks insertion by checking all of the store's objects
        r = self.client.get(newt_base_url + "/stores/" + store_id + "/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output'][0], payload['data'])
        # Checks insertion by checking the individual object
        r = self.client.get(newt_base_url + "/stores/" + store_id + "/" + obj_id + "/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output'], payload['data'])
        
        # Tests update
        updated_payload = {"data": json.dumps({"foo": "baz"})}
        r = self.client.put(newt_base_url + "/stores/" + store_id + "/" + obj_id + "/",
                         data=json.dumps(updated_payload), content_type="application/json")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output'], updated_payload['data'])

        # Tests delete
        r = self.client.delete(newt_base_url + "/stores/" + store_id + "/")
        self.assertEquals(r.status_code, 200)

    def test_stores_creation_with_initial(self):
        payload = {"data": json.dumps({"x":5})}

        # Without an initial name
        r = self.client.post(newt_base_url + "/stores", data=payload)
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        store_id = json_response['output']['id']
        self.assertEquals(json_response['output']['oid'][0], 0)

        # With an initial name
        r = self.client.post(newt_base_url + "/stores/teststore1/", data=payload)
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['id'], "teststore1")

        r = self.client.delete(newt_base_url + "/stores/teststore1/")
        self.assertEquals(r.status_code, 200)
        r = self.client.delete(newt_base_url + "/stores/" + store_id + "/")
        self.assertEquals(r.status_code, 200)

    def test_store_perms(self):
        login = { 'username': "testuser", 'password': "test1pass" }

        self.client.post(newt_base_url + "/auth", data=login)

        r = self.client.post(newt_base_url + "/stores/test_store_1/")
        self.assertEquals(r.status_code, 200)
        r = self.client.get(newt_base_url + "/stores/test_store_1/perms/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['name'], "test_store_1")
        self.assertEquals(json_response['output']['users'][0]['name'], "testuser")

        payload = {"data": json.dumps([{"name": "tsun", "perms": ["r"]}])}
        r = self.client.post(newt_base_url + "/stores/test_store_1/perms/", data=payload)
        self.assertEqual(r.status_code, 200)

        r = self.client.get(newt_base_url + "/stores/test_store_1/perms/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['name'], "test_store_1")
        self.assertEquals(json_response['output']['users'][1]['name'], "tsun")
        self.assertEquals(json_response['output']['users'][1]['perms'], ['r'])

        payload = {"data": json.dumps([{"name": "tsun", "perms": ["r", "w"]}])}
        r = self.client.post(newt_base_url + "/stores/test_store_1/perms/", data=payload)

        r = self.client.get(newt_base_url + "/stores/test_store_1/perms/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['name'], "test_store_1")
        self.assertEquals(json_response['output']['users'][1]['name'], "tsun")
        self.assertEquals(json_response['output']['users'][1]['perms'], ['r', 'w'])

        self.client.delete(newt_base_url + "/stores/test_store_1/")
        r = self.client.get(newt_base_url + "/stores/test_store_1/perms/")
        self.assertEquals(r.status_code, 404)

class AcctTests(TestCase):
    fixtures = ["test_fixture.json"]

    def setUp(self):
        self.client = MyTestClient()

    def test_info_ret(self):
        r = self.client.get(newt_base_url + "/account/user/testuser/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['username'], 'testuser')

        r = self.client.get(newt_base_url + "/account/user/id/2/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['username'], 'testuser')

        r = self.client.get(newt_base_url + "/account/group/id/1/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['name'], "Test Group")


class JobTests(TestCase):

    def setUp(self):
        self.client = MyTestClient()

    def test_running_cmds(self):
        # Tests getting queues
        r = self.client.get(newt_base_url + "/queue/")
        self.assertEquals(r.status_code, 200)

        # Tests submitting a job
        payload = {
            "jobscript": "sleep 5\nls ~"
        }
        r = self.client.post(newt_base_url + "/queue/localhost/", data=payload)
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertIsNot(json_response['output']['jobid'], None)
        job_id = json_response['output']['jobid']

        # Tests getting job info
        r = self.client.get(newt_base_url + "/queue/localhost/%s/" % job_id)
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['jobid'], job_id)

        # Delete job from queue
        r = self.client.delete(newt_base_url + "/queue/localhost/%s/" % job_id)
        self.assertEquals(r.status_code, 200)