"""
    Database Structure:

        "stores" - A list of all of the stores in the database

        For every store: 
            <store_name>:docs - A list of all of the documents within the store
            <store_name>:perms - A list of all of the permissions of the store

        Documents:
            <store_name>:<document_id>

        Permissions: 
            <store_name>:perms:<username> ['r','w']
"""


from common.response import json_response
import logging
logger = logging.getLogger("newt." + __name__)

import redis
import re
import json
import random, string, uuid

STOREDB = 0
HOST = "localhost"

def get_stores(request):
    """Returns a list of available store names.

    Keyword arguments:
    request -- Django HttpRequest object
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)
    return storedb.lrange("stores",0,-1)

def create_store(request, store_name=None, initial_data=[]):
    """Creates a store with the given store_name and initial_data; Returns a 
    dictionary in the form of:
    {
        "id": <store_name>, 
        "oid": <list_of_initial_data_ids>
    }

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store (optional)
    initial_data -- Array of data to be stored (optional)
    
    Note: if the store_name is not set, the implementation should create a name
    for the store.
    """

    storedb = redis.Redis(host=HOST, db=STOREDB)
    
    if not store_name:
        store_name = random.choice(string.ascii_letters) + str(uuid.uuid4())[0:8]
        while(store_name in get_stores(request)):
            store_name = str(uuid.uuid4())[0:8]
    elif store_name in get_stores(request):
        return json_response(status="ERROR", status_code=400, error="Store name already exists.")
    
    oid_list = []
    for oid, data in enumerate(initial_data):
        dbname = store_name + ":" + str(oid)
        storedb.set(dbname, data)
        storedb.rpush(store_name + ":docs", dbname)
        oid_list.append(str(oid))

    storedb.rpush("stores", store_name)
    storedb.rpush(store_name + ":perms", store_name + ":perms:" + request.user.username)

    #set initial perms to read and write
    storedb.rpush(store_name + ":perms:" + request.user.username, "r")
    storedb.rpush(store_name + ":perms:" + request.user.username, "w")

    # returns store_name

    return {"id": store_name, "oid": oid_list}

def get_store_contents(request, store_name):
    """Returns a list containing all the contents of the store in the form of:
    [
        {
            "oid": <document_id>,
            "data": <document_data>,
        },
        ...
    ]

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)
    if store_name not in get_stores(request):
        return json_response(status="ERROR", status_code=404, error="Store does not exist.")    
    store_docs = storedb.lrange(store_name + ":docs",0,-1)
    store_contents = []
    for doc in store_docs:
        store_contents.append({
            "oid":doc[len(store_name)+1:],
            "data":storedb.get(doc),
        })
    return store_contents

def query_store(request, store_name, query):
    """Queries the store; Returns the result of the query in the form of:
    [
        {
            "oid": <document_id>,
            "data": <document_data>,
        },
        ...
    ]

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    query -- a query string
    """
    if store_name not in get_stores(request):
        return json_response(status="ERROR", status_code=404, error="Store does not exist.")    
    return json_response(status="ERROR", status_code=501, error="Method not implemented.")
    # return storedb.get(storedb+":"+query)

def store_get_obj(request, store_name, obj_id):
    """Returns the data of the specified document in the store.

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    obj_id -- ID of the object in the store
    """
    storedb = redis.Redis(host=HOST, db = STOREDB)
    
    if store_name not in get_stores(request):
        return json_response(status="ERROR", status_code=404, error="Store does not exist.")    
    
    return storedb.get(store_name + ":" + obj_id)

def store_insert(request, store_name, initial_data):
    """Creates a new document in the store with initial_data; Returns the oid 
    of the new document.

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    initial_data -- document data
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

    return str(index_num)

def store_update(request, store_name, obj_id, data):
    """Updates the contents of a given document; Returns the oid of the 
    document.

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    obj_id -- ID of the object in the store
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)

    if store_name not in get_stores(request):
        return json_response(status="ERROR", status_code=404, error="Store does not exist.")    
    
    # Get data from PUT request
    
    storedb.set(store_name + ":" + obj_id, data)

    return obj_id

def get_store_perms(request, store_name):
    """Returns a dictionary of permissions of the store in the form of:
    {
        "name": <store_name>,
        "perms": [
            {
                "user": <associated_user>,
                "perms": <permissions_of_user>,
            },
            ...
        ],
    }

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)
    if store_name not in get_stores(request):
        return json_response(status="ERROR", status_code=404, error="Store does not exist.")    
    
    all_perm_entries = storedb.lrange(store_name+":perms", 0, -1)
    perms_list = []

    for entry in all_perm_entries:
        perms_list.append({
            "name": entry[len(store_name) + 7:],
            "perms": storedb.lrange(entry,0,-1)
        })

    return {"name": store_name, "perms": perms_list,}

def update_store_perms(request, store_name, perms):
    """Updates the permissions of the given store with perms; Returns the id of
    the store.

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    perms -- list of the new permissions in the form of:
        [
            {
                "user": <user_to_be_updated>,
                "perms": <updated_perms>,
            },
            ...
        ]
    """
    storedb = redis.Redis(host=HOST, db=STOREDB)
    if store_name not in get_stores(request):
        return json_response(status="ERROR", status_code=404, error="Store does not exist.")    
    
    new_perms = []

    for new_perm in perms:
        dbname = store_name + ":perms:" + new_perm['name']
        if storedb.lrange(dbname, 0, -1):
            storedb.delete(dbname)
        for perm in new_perm['perms']:
            storedb.rpush(dbname, perm)
        new_perms.append({
            "user": new_perm['name'],
            "perms": storedb.lrange(dbname,0,-1),
        })

    return new_perms

def delete_store(request, store_name):
    """Deletes the store with a given store_name; Returns the id of the deleted
    store.

    Keyword arguments:
    store_name -- the name of the store
    """
    # Search for store: if doesn't exist, return different message

    storedb = redis.Redis(host=HOST, db=STOREDB)

    if store_name not in get_stores(request):
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
    return store_name

patterns = (
)

def extras_router(request, query):
    """Maps a query to a function if the pattern matches and returns result

    Keyword arguments:
    request -- Django HttpRequest
    query -- the query to be matched against
    """
    for pattern, func, req in patterns:
        match = pattern.match(query)
        if match and req:
            return func(request, **match.groupdict())
        elif match:
            return func(**match.groupdict())

    # Returns an Unimplemented response if no pattern matches
    return json_response(status="Unimplemented", 
                             status_code=501, 
                             error="", 
                             content="query: %s" % query)
