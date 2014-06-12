"""Mongo Adapter for NEWT 

Structure:
    - Database Name: stores
    - Each new store is a new collection in the database 
    - Each object in the collection is stored as:
        {
            "_id": Mongo ObjectId
            "oid": Id of the object stored (str)
            "data": The object data
        }
    - Permissions (?) are stored in the 'permissions' collection as:
        {
            "name": Name of the store 
            "groups": Groups associated with the store 
            "owner": Owner of the store
            "users": Users with access to the store as:
                {
                    "name": ...
                    "perms": ['r', 'w', ... ]
                }
        }

"""
from pymongo import MongoClient
from common.response import json_response
import json
import uuid, random, string
from django.http import QueryDict
import logging
logger = logging.getLogger(__name__)

def get_stores():
    """Returns a list of available stores"""
    db = MongoClient()['stores']
    return filter(lambda s: s!="system.indexes", db.collection_names())

def create_store(request, store_name):
    """Creates a store with the given store_name and initial_data

    Keyword arguments:
    request -- request the data can be derived from
    store_name -- the name of the store
    """
    # Check that store name is unique (or create unique identifier)
    if not store_name:
        store_name = random.choice(string.ascii_letters) + str(uuid.uuid4())[0:8]
        while(store_name in get_stores()):
            store_name = str(uuid.uuid4())[0:8]
    elif store_name in get_stores():
        return json_response(status="ERROR", status_code=400, error="Store name already exists.")
    
    # Loads the initial data if it exists
    initial_data = json.loads(request.POST.get("data", "[]"))

    # Create new collection
    db = MongoClient()['stores']
    new_collection = db.create_collection(store_name)
    
    # Load initial data into the store
    oid_list = []
    for oid, data in enumerate(initial_data):
        new_collection.insert({"oid": str(oid), "data": data})
        oid_list.append(oid)
    # Add entry to permissions
    perms = db['permissions']
    perms.insert({
        "name": store_name,
        "groups": [],
        "owner": request.user.username,
        "users": [{
            "name": request.user.username,
            "perms": ['r', 'w'],
        }],
    })
    # Return the name of the store/status/objects created
    return {"id": new_collection.name, "oid": oid_list}

def delete_store(store_name):
    """Deletes the store with a given store_name

    Keyword arguments:
    store_name -- the name of the store
    """
    # Check privlages of user attempting to delete store
    # Delete store
    # Return the status/output of the operation
    db = MongoClient()['stores']
    store = db[store_name]
    store.drop()
    perms = db['permissions']
    perms.find_and_modify({"name": store_name}, remove=True)
    return {"dropped": store_name}

def get_store_contents(store_name):
    """Returns a list containing all the contents of the store

    Keyword arguments:
    store_name -- the name of the store
    """
    # Check existance of the store
    if store_name not in get_stores():
        return json_response(status="ERROR", 
                             status_code=404, 
                             error="Store does not exist: %s" % store_name)

    # Check privlages of user attempting to access store

    # Get and return contents of the store
    db = MongoClient()['stores']
    store = db[store_name]
    return [x['data'] for x in store.find({}, {"_id":0, "data":1})]

def query_store(store_name, query):
    """Returns the result of querying the given store with query

    Keyword arguments:
    store_name -- the name of the store
    query -- a query string
    """
    # Check privlages of user attempting to acccess store
    # Run query on the given store and return results
    pass

def get_store_perms(store_name):
    """Returns a dictionary of permissions of the store

    Keyword arguments:
    store_name -- the name of the store
    """
    # Return the permissions of the store
    db = MongoClient()['stores']
    store = db["permissions"]
    res = store.find_one({"name":store_name}, {"_id":0})
    if res:
        return res
    else:
        return json_response(status="ERROR", status_code="404", error="Store not found")

def update_store_perms(request, store_name):
    """Updates the permissions of the given store with perms

    Keyword arguments:
    store_name -- the name of the store
    perms -- dictionary of the updated permissions
            [
                {
                    "name": ..., 
                    "perms": [...]
                }, 
                ... 
            ]
    """
    # Gets updated permissions from the request
    perms = request.POST.get("data", None)
    if not perms:
        return json_response(status="ERROR", status_code=400, error="No data received.")

    # Updates the permissions of the store and returns the status
    db = MongoClient()['stores']
    perm_col = db['permissions']
    for new_perm in json.loads(perms):
        # Remove original permission
        perm_col.update({"name": store_name}, {"$pull": {"users": {"name": new_perm['name']}}})
        # Insert new permission
        perm_col.update({"name": store_name}, {"$addToSet":{"users": new_perm}})
    return {"id": store_name}

def store_insert(request, store_name):
    """Inserts data into the store

    Keyword arguments:
    store_name -- the name of the store
    data -- a list of key value pairs to be put in the store
    """
    # Get the data
    data = request.POST.get("data", None)
    if not data:
        return json_response(status="ERROR", status_code=400, error="No data received.")

    # Insert the key value pairs into the store
    db = MongoClient()['stores']
    store = db[store_name]
    oid = str(store.count())
    store.insert({"oid": oid, "data": data})
    return {"id": oid}

def store_update(request, store_name, obj_id):
    """Updates a certain key-value pair in the store

    Keyword arguments:
    store_name -- the name of the store
    pair -- the updated pair (dict)
    """
    # Get data from PUT request
    data = QueryDict(request.body).get("data", None)
    if not data:
        return json_response(status="ERROR", status_code=400, error="No data received.")

    # Set the key of the store to the new value
    db = MongoClient()['stores']
    store = db[store_name]
    store.update({"oid":obj_id},{"$set":{"data": data}})
    return data

def store_get_obj(store_name, obj_id):
    """Gets the value of the specified key in the store 

    Keyword arguments:
    store_name -- the name of the store
    key -- the key at which the value is store in the store
    """
    # Gets the value of the key in the store
    db = MongoClient()['stores']
    store = db[store_name]
    obj = store.find_one({"oid":obj_id},{"_id":0, "data":1})
    if obj:
        return obj['data']
    else:
        return json_response(status="ERROR",
                             status_code=400,
                             error="Object not found: %s - Object %s" 
                                    % (store_name, obj_id))

