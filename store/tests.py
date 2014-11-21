from django.test import TestCase
from django.conf import settings
import json
from newt.tests import MyTestClient, newt_base_url, login


class StoreTests(TestCase):
    fixtures = ["test_fixture.json"]

    def setUp(self):
        self.client = MyTestClient()
        # Hacky: Need to figure out a way around this...
        try:
            from pymongo import MongoClient
            db = MongoClient()['store']
            db.test_store_1.drop()
            db.permissions.remove({"name":"test_store_1"})
        except Exception:
            pass
        try:
            import redis
            storedb = redis.Redis(host="localhost", db=0)
            storedb.flushdb()
        except Exception:
            pass

    def test_store_basic(self):
        self.client.post(newt_base_url + "/auth", data=login)

        r = self.client.get(newt_base_url + "/store")
        self.assertEquals(r.status_code, 200)

    def test_store_manipulation(self):
        self.client.post(newt_base_url + "/auth", data=login)

        # Creates a new store (create_store)
        r = self.client.post(newt_base_url + "/store")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()

        # Ensures that no data was added to the store
        self.assertEquals(json_response['output']['oid'], [])
        store_id = json_response['output']['id']
        
        # Ensures that new store is empty (get_store_contents)
        r = self.client.get(newt_base_url + "/store/" + store_id + "/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output'], [])
        
        # Tests insertion (store_insert)
        payload = {"data": json.dumps({"foo":"bar"})}
        r = self.client.post(newt_base_url + "/store/" + store_id + "/",
                          data=payload)
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        obj_id = json_response['output']

        # Checks insertion by checking all of the store's objects (get_store_contents)
        r = self.client.get(newt_base_url + "/store/" + store_id + "/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output'][0]['data'], payload['data'])
        self.assertEquals(json_response['output'][0]['oid'], obj_id)

        # Checks insertion by checking the individual object (store_get_obj)
        r = self.client.get(newt_base_url + "/store/" + store_id + "/" + obj_id + "/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output'], payload['data'])
        
        # Tests update (store_update)
        updated_payload = {"data": json.dumps({"foo": "baz"})}
        r = self.client.put(newt_base_url + "/store/" + store_id + "/" + obj_id + "/",
                         data=json.dumps(updated_payload), content_type="application/json")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output'], obj_id)

        # Checks updated data
        r = self.client.get(newt_base_url + "/store/" + store_id + "/" + obj_id + "/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output'], updated_payload['data'])

        # Tests delete
        r = self.client.delete(newt_base_url + "/store/" + store_id + "/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEqual(json_response['output'], store_id)

        # Ensures that getting the deleted store will error
        r = self.client.get(newt_base_url + "/store/" + store_id + "/")
        self.assertEquals(r.status_code, 404)        

    def test_store_creation_with_initial(self):
        self.client.post(newt_base_url + "/auth", data=login)

        payload = {"data": json.dumps({"x":5})}

        # Without an initial name
        r = self.client.post(newt_base_url + "/store/", data=payload)
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        store_id = json_response['output']['id']
        self.assertEquals(len(json_response['output']['oid']), 1)
        obj_id = json_response['output']['oid'][0]

        # Checks the data
        r = self.client.get(newt_base_url + "/store/" + store_id + "/" + obj_id + "/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output'], payload['data'])


        # With an initial name
        r = self.client.post(newt_base_url + "/store/teststore1/", data=payload)
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['id'], "teststore1")
        self.assertEquals(len(json_response['output']['oid']), 1)
        obj_id = json_response['output']['oid'][0]

        # Checks the data
        r = self.client.get(newt_base_url + "/store/teststore1/" + obj_id + "/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output'], payload['data'])

        # Deletes the store
        r = self.client.delete(newt_base_url + "/store/teststore1/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEqual(json_response['output'], "teststore1")
        r = self.client.delete(newt_base_url + "/store/" + store_id + "/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEqual(json_response['output'], store_id)

    def test_store_perms(self):
        self.client.post(newt_base_url + "/auth", data=login)

        # Create a store
        r = self.client.post(newt_base_url + "/store/test_store_1/")
        self.assertEquals(r.status_code, 200)
        r = self.client.get(newt_base_url + "/store/test_store_1/perms/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        # Checks that the creator has appropriate permissions
        self.assertEquals(json_response['output']['name'], "test_store_1")
        self.assertEquals(json_response['output']['perms'][0]['name'], login['username'])
        self.assertIn("r", json_response['output']['perms'][0]['perms'])
        self.assertIn("w", json_response['output']['perms'][0]['perms'])

        payload = {"data": json.dumps([{"name": login['username'], "perms": ["r", "w", "x"]}])}
        r = self.client.post(newt_base_url + "/store/test_store_1/perms/", data=payload)
        self.assertEqual(r.status_code, 200)

        r = self.client.get(newt_base_url + "/store/test_store_1/perms/")
        self.assertEquals(r.status_code, 200)
        json_response = r.json()
        self.assertEquals(json_response['output']['name'], "test_store_1")
        self.assertEquals(json_response['output']['perms'][0]['name'], login['username'])
        self.assertIn("r", json_response['output']['perms'][0]['perms'])
        self.assertIn("w", json_response['output']['perms'][0]['perms'])
        self.assertIn("x", json_response['output']['perms'][0]['perms'])

        # Deletes the store
        r = self.client.delete(newt_base_url + "/store/test_store_1/")
        self.assertEquals(r.status_code, 200)
        r = self.client.get(newt_base_url + "/store/test_store_1/perms/")
        self.assertEquals(r.status_code, 404)
