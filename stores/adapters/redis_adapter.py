"""
    Permissions: 
        store_name:perms:name ['r','w']
"""


from common.response import json_response
import logging
logger = logging.getLogger(__name__)

import redis
import re

STOREDB = 0
HOST = "localhost"


"""
    Database names will be store:store_name
"""


def get_stores():
    """Returns a list of available stores"""
    storedb = redis.Redis(host=HOST, db=STOREDB)
    return storedb.lrange("stores",0,-1)

def create_store(request, store_name):
    """Creates a store with the given store_name and initial_data

    Keyword arguments:
    request -- request the data can be derived from
    store_name -- the name of the store
    """
    # Check to see that the store name is unique
    # Returns store_name and data

    storedb = redis.Redis(host=HOST, db=STOREDB)
    
    # Throw an exception if the store_name already exists
    if store_name in get_stores():
        raise Exception("Store already exists.")

    # Gets initial data if it exists
    initial_data = json.loads(request.POST.get("data","[]"))
    
    for oid, data in enumerate(initial_data):
        dbname = store_name + ":" + str(oid)
        storedb.set(dbname, data)
        storedb.rpush(store_name + ":docs", dbname)

    storedb.rpush("stores", store_name)
    storedb.rpush(store_name + ":perms", store_name + ":perms:" + request.user.username)

    #set initial perms to read and write
    storedb.set(store_name + ":perms:" + request.user.username, "r")
    storedb.set(store_name + ":perms:" + request.user.username, "w")

    # returns store_name

    return {"store_name": store_name}

def delete_store(store_name):
    """Deletes the store with a given store_name

    Keyword arguments:
    store_name -- the name of the store
    """
    # Search for store: if doesn't exist, return different message

    storedb = redis.Redis(host=HOST, db=STOREDB)

    if store_name not in get_stores():
        return {"msg": store_name + " does not exist in the database"}
    

    store_docs = storedb.lrange(store_name + ":docs",0,-1)
    for entry in all_entries:
        storedb.delete(entry)

    storedb.delete(store_name + ":docs")
    storedb.lrem("stores", 1, store_name)

    # Returns message indicating the successful deletion
    return {"msg": store_name + " has successfully been deleted"}


def get_store_contents(store_name):
    """Returns a list containing all the contents of the store

    Keyword arguments:
    store_name -- the name of the store
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)

    

def query_store(store_name, query):
    """Returns the result of querying the given store with query

    Keyword arguments:
    store_name -- the name of the store
    query -- a query string
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)

    return storedb.get(storedb+":"+query)

def get_store_perms(store_name):
    """Returns a dictionary of permissions of the store

    Keyword arguments:
    store_name -- the name of the store
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)
    all_perm_entries = storedb.keys(store_name+":perms:*")
    perms_dict = {}

    for entry in all_perm_entries:
        perms_dict[entry[len(store_name) + 7:]] = storedb.lget(entry,0,-1)

    return perms_dict


def update_store_perms(request, store_name):
    """Updates the permissions of the given store with perms

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)
    perms = request.POST.get("data", None)
    if not perms:
        return json_response(status="ERROR", status_code=400, error="No data received.")
    for new_perm in json.loads(perms):
        dbname = store_name + ":perms:" + new_perm['name']
        if storedb.lrange(dbname, 0, -1):
            storedb.delete(dbname)
        for perm in new_perm['perms']:
            storedb.rpush(dbname, perm)

    return {'msg': 'Permissions updated'}


def store_insert(request, store_name):
    """Inserts data into the store

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    """

    

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

