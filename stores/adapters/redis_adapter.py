"""
    Permissions: 
        store_name:perms:name ['r','w']
"""


from common.response import json_response
import logging
logger = logging.getLogger(__name__)

import redis
import re
import json
import random, string, uuid

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
    
    if not store_name:
        store_name = random.choice(string.ascii_letters) + str(uuid.uuid4())[0:8]
        while(store_name in get_stores()):
            store_name = str(uuid.uuid4())[0:8]
    elif store_name in get_stores():
        return json_response(status="ERROR", status_code=400, error="Store name already exists.")
    

    # Gets initial data if it exists
    initial_data = json.loads(request.POST.get("data","[]"))
    
    oid_list = []
    for oid, data in enumerate(initial_data):
        dbname = store_name + ":" + str(oid)
        storedb.set(dbname, data)
        storedb.rpush(store_name + ":docs", dbname)
        oid_list.append(oid)

    storedb.rpush("stores", store_name)
    storedb.rpush(store_name + ":perms", store_name + ":perms:" + request.user.username)

    #set initial perms to read and write
    storedb.rpush(store_name + ":perms:" + request.user.username, "r")
    storedb.rpush(store_name + ":perms:" + request.user.username, "w")

    # returns store_name

    return {"id": store_name, "oid": oid_list}

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
    for doc in store_docs:
        storedb.delete(doc)

    store_perms = storedb.lrange(store_name + ":perms",0,-1)
    for perm in store_perms:
        storedb.delete(perm)

    storedb.delete(store_name + ":docs")
    storedb.delete(store_name + ":perms")
    storedb.lrem("stores", store_name, 1)

    # Returns message indicating the successful deletion
    return {"msg": store_name + " has successfully been deleted"}


def get_store_contents(store_name):
    """Returns a list containing all the contents of the store

    Keyword arguments:
    store_name -- the name of the store
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)
    if store_name not in get_stores():
        return json_response(status="ERROR", status_code=404, error="Store does not exist.")    
    store_docs = storedb.lrange(store_name + ":docs",0,-1)
    store_contents = []
    for doc in store_docs:
        store_contents.append(storedb.get(doc))
    return store_contents

def query_store(store_name, query):
    """Returns the result of querying the given store with query

    Keyword arguments:
    store_name -- the name of the store
    query -- a query string
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)
    if store_name not in get_stores():
        return json_response(status="ERROR", status_code=404, error="Store does not exist.")    
    
    return storedb.get(storedb+":"+query)

def get_store_perms(store_name):
    """Returns a dictionary of permissions of the store

    Keyword arguments:
    store_name -- the name of the store
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)
    if store_name not in get_stores():
        return json_response(status="ERROR", status_code=404, error="Store does not exist.")    
    
    all_perm_entries = storedb.lrange(store_name+":perms", 0, -1)
    perms_list = []

    for entry in all_perm_entries:
        perms_list.append({
            "name": entry[len(store_name) + 7:],
            "perms": storedb.lrange(entry,0,-1)
        })

    return {"name": store_name, "users": perms_list,}


def update_store_perms(request, store_name):
    """Updates the permissions of the given store with perms

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)
    if store_name not in get_stores():
        return json_response(status="ERROR", status_code=404, error="Store does not exist.")    
    
    perms = request.POST.get("data", None)
    if not perms:
        return json_response(status="ERROR", status_code=400, error="No data received.")
    for new_perm in json.loads(perms):
        dbname = store_name + ":perms:" + new_perm['name']
        if storedb.lrange(dbname, 0, -1):
            storedb.delete(dbname)
        for perm in new_perm['perms']:
            storedb.rpush(dbname, perm)

    return {'id': store_name}


def store_insert(request, store_name):
    """Inserts data into the store

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)
    # Creating next docname
    index_num = len(storedb.lrange(store_name + ":docs", 0, -1))
    docname = store_name + ":" + str(index_num)
    # Getting data

    data = request.POST.get("data", None)
    if not data:
        return json_response(status="ERROR", status_code=400, error="No data received.")


    storedb.set(docname, data)
    storedb.rpush(store_name + ":docs", docname)

    # Return success message
    return {'id': str(index_num)}
    

def store_update(request, store_name, obj_id):
    """Updates a certain key-value pair in the store

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    obj_id -- ID of the object in the store
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)

    if store_name not in get_stores():
        return json_response(status="ERROR", status_code=404, error="Store does not exist.")    
    
    # Get data from PUT request
    data = json.loads(request.body).get("data", None)
    if not data:
        return json_response(status="ERROR", status_code=400, error="No data received.")

    storedb.set(store_name + ":" + obj_id, data)

    return data


def store_get_obj(store_name, obj_id):
    """Gets the value of the specified key in the store 

    Keyword arguments:
    store_name -- the name of the store
    obj_id -- ID of the object in the store
    """
    storedb = redis.Redis(host=HOST, db = STOREDB)
    
    if store_name not in get_stores():
        return json_response(status="ERROR", status_code=404, error="Store does not exist.")    
    
    return storedb.get(store_name + ":" + obj_id)

