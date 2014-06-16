"""Store Adapter Template File

IMPORTANT: NOT A FUNCTIONAL ADAPTER. FUNCTIONS MUST BE IMPLEMENTED

Notes:
    - Each of the functions defined below must return a json serializable
      object, json_response, or valid HttpResponse object
    - A json_response creates an HttpResponse object given parameters:
        - content: string with the contents of the response 
        - status: string with the status of the response 
        - status_code: HTTP status code 
        - error: string with the error message if there is one 
"""
from common.response import json_response
import logging
logger = logging.getLogger(__name__)

import redis

STOREDB = 0
HOST = "localhost"

def get_stores():
    """Returns a list of available stores"""
    return redis.Redis(host=HOST, db=STOREDB).keys('store')

def create_store(request, store_name):
    """Creates a store with the given store_name and initial_data

    Keyword arguments:
    request -- request the data can be derived from
    store_name -- the name of the store
    """
    # Check to see that the store name is unique
    # Returns store_name and data

    # Gets initial data if it exists
    initial_data = json.loads(request.POST.get("data","[]"))

    if store_name in get_stores():
        raise Exception("Store already exists.")
    storedb = redis.Redis(host=HOST, db=STOREDB)
    storedb.set("store:" + store_name, initial_data)
    return {"store_name": store_name, "data": initial_data}

def delete_store(store_name):
    """Deletes the store with a given store_name

    Keyword arguments:
    store_name -- the name of the store
    """
    pass

def get_store_contents(store_name):
    """Returns a list containing all the contents of the store

    Keyword arguments:
    store_name -- the name of the store
    """
   pass

def query_store(store_name, query):
    """Returns the result of querying the given store with query

    Keyword arguments:
    store_name -- the name of the store
    query -- a query string
    """
    pass

def get_store_perms(store_name):
    """Returns a dictionary of permissions of the store

    Keyword arguments:
    store_name -- the name of the store
    """
    pass

def update_store_perms(request, store_name):
    """Updates the permissions of the given store with perms

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    """
    pass

def store_insert(request, store_name):
    """Inserts data into the store

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    """
    pass

def store_update(request, store_name, obj_id):
    """Updates a certain key-value pair in the store

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    obj_id -- ID of the object in the store
    """
    pass

def store_get_obj(store_name, obj_id):
    """Gets the value of the specified key in the store 

    Keyword arguments:
    store_name -- the name of the store
    obj_id -- ID of the object in the store
    """
    pass

