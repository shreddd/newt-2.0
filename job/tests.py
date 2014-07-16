from django.test import TestCase
from django.conf import settings
import json
import time
import os
from newt.tests import MyTestClient, newt_base_url, login

try:
    from newt.local_settings import test_machine as machine
except ImportError:
    machine = "localhost"

class JobTests(TestCase):
    fixtures = ["test_fixture.json"]
    

    def setUp(self):
        self.client = MyTestClient()
        self.client.post(newt_base_url + "/auth", data=login)

    def test_get_queues(self):
        # Tests getting queues
        r = self.client.get(newt_base_url + "/job/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertTrue(len(json_response['output']) > 0)
        self.assertIn(machine, json_response['output'].keys())

    def test_running_cmds(self):
        # Tests submitting a job
        payload = {
            "jobscript": "sleep 5"
        }
        r = self.client.post(newt_base_url + "/job/"+machine+"/", data=payload)
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertIsNot(json_response['output']['jobid'], None)

        # Get job id from submitting the job
        job_id = json_response['output']['jobid']

        # Tests getting job info
        r = self.client.get(newt_base_url + "/job/"+machine+"/%s/" % job_id)
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['jobid'], job_id)
        self.assertEquals(json_response['output']['user'], login['username'])
        
        # Delete job from queue
        r = self.client.delete(newt_base_url + "/job/"+machine+"/%s/" % job_id)
        self.assertEquals(r.status_code, 200)

    # def test_short_cmd(self):
    #     payload = {
    #         "jobscript": "ls -a /"
    #     }
    #     r = self.client.post(newt_base_url + "/job/"+machine+"/", data=payload)
    #     self.assertEquals(r.status_code, 200)
    #     json_response = r.json()
    #     self.assertIsNot(json_response['output']['jobid'], None)
    #     job_id = json_response['output']['jobid']

    #     time.sleep(1)

    #     r = self.client.get(newt_base_url + "/job/"+machine+"/%s/" % job_id)
    #     self.assertEquals(r.status_code, 200)
    #     json_response = r.json()
    #     self.assertEquals(json_response['output']['jobid'], job_id)
    #     self.assertEquals(json_response['output']['user'], login['username'])
    #     self.assertEquals(json_response['output']['status'], '0')
    #     files = ['.', '..'] + os.listdir("/")
    #     files.sort()
    #     cmd_out = json_response['output']['output'].splitlines()
    #     self.assertEquals(files, cmd_out)
