from django.test import TestCase
from django.conf import settings
import json
import os
import socket
from newt.tests import MyTestClient, newt_base_url, login
from unittest import skipIf
try:
    from local_settings import test_machine as machine
except ImportError:
    machine = "localhost"


class CommandTests(TestCase):
    def setUp(self):
        self.client = MyTestClient()

    def test_root(self):
        r = self.client.get(newt_base_url+'/command')
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['status'], "OK")
        self.assertIn(machine, json_response['output'])

    def test_command(self):
        r = self.client.post(newt_base_url+'/command/'+machine, {'command': '/bin/hostname'})
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['status'], "OK")

        hostname = socket.gethostname()
        self.assertEquals(hostname, json_response['output']['output'].strip())

    @skipIf(machine != "localhost", "Can't run ls on remote machine")
    def test_command_with_args(self):
        # Run ls in / 
        r = self.client.post(newt_base_url+'/command/'+machine, {'command': '/bin/ls -a /'})
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['status'], "OK")
        # os.listdir() leaves off . and .. so add them in
        files = ['.', '..'] + os.listdir('/')
        files.sort()
        newtfiles = json_response['output']['output'].strip().split('\n')
        newtfiles.sort()
        self.assertEquals(files, newtfiles)
