"""Mongo Adapter for NEWT 

Structure:
    - Database Name: store
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
logger = logging.getLogger("newt." + __name__)

def get_store(request):
    """Returns a list of available store names.

    Keyword arguments:
    request -- Django HttpRequest object
    """
    db = MongoClient()['store']
    return filter(lambda s: s!="system.indexes", db.collection_names())

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
    # Check that store name is unique (or create unique identifier)
    if not store_name:
        store_name = random.choice(string.ascii_letters) + str(uuid.uuid4())[0:8]
        while(store_name in get_store(request)):
            store_name = str(uuid.uuid4())[0:8]
    elif store_name in get_store(request):
        return json_response(status="ERROR", status_code=400, error="Store name already exists.")
    
    # Create new collection
    db = MongoClient()['store']
    new_collection = db.create_collection(store_name)
    
    # Load initial data into the store
    oid_list = []
    for oid, data in enumerate(initial_data):
        new_collection.insert({"oid": str(oid), "data": data})
        oid_list.append(str(oid))
    # Add entry to permissions
    perms = db['permissions']
    perms.insert({
        "name": store_name,
        "owner": request.user.username,
        "perms": [{
            "name": request.user.username,
            "perms": ['r', 'w'],
        }],
    })
    # Return the name of the store/status/objects created
    return {"id": new_collection.name, "oid": oid_list}

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
    # Check existance of the store
    if store_name not in get_store(request):
        return json_response(status="ERROR", 
                             status_code=404, 
                             error="Store does not exist: %s" % store_name)

    # Check privlages of user attempting to access store

    # Get and return contents of the store
    db = MongoClient()['store']
    store = db[store_name]
    return [{"oid": x["oid"], "data": x['data']} for x in store.find({}, {"_id":0, "data":1, "oid":1})]

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
    return json_response(status="ERROR", status_code=501, error="Unimplemented")

def store_get_obj(request, store_name, obj_id):
    """Returns the data of the specified document in the store.

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    obj_id -- ID of the object in the store
    """
    # Gets the value of the key in the store
    db = MongoClient()['store']
    store = db[store_name]
    obj = store.find_one({"oid":obj_id},{"_id":0, "data":1})
    if obj:
        return obj['data']
    else:
        return json_response(status="ERROR",
                             status_code=400,
                             error="Object not found: %s - Object %s" 
                                    % (store_name, obj_id))

def store_insert(request, store_name, initial_data):
    """Creates a new document in the store with initial_data; Returns the oid 
    of the new document.

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    initial_data -- document data
    """
    # Get the data
    data = initial_data
    if not data:
        return json_response(status="ERROR", status_code=400, error="No data received.")

    # Insert the key value pairs into the store
    db = MongoClient()['store']
    store = db[store_name]
    oid = str(store.count())
    store.insert({"oid": oid, "data": data})
    return oid

def store_update(request, store_name, obj_id, data):
    """Updates the contents of a given document; Returns the oid of the 
    document.

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    obj_id -- ID of the document in the store
    data -- Updated data of the document
    """
    # Set the key of the store to the new value
    db = MongoClient()['store']
    store = db[store_name]
    store.update({"oid":obj_id},{"$set":{"data": data}})
    return str(obj_id)

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
    # Return the permissions of the store
    db = MongoClient()['store']
    store = db["permissions"]
    res = store.find_one({"name":store_name}, {"_id":0})
    if res:
        return res
    else:
        return json_response(status="ERROR", status_code="404", error="Store not found")

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
    # Updates the permissions of the store and returns the status
    db = MongoClient()['store']
    perm_col = db['permissions']
    for new_perm in perms:
        # Remove original permission
        perm_col.update({"name": store_name}, {"$pull": {"perms": {"name": new_perm['name']}}})
        # Insert new permission
        perm_col.update({"name": store_name}, {"$addToSet":{"perms": new_perm}})
    return store_name

def delete_store(request, store_name):
    """Deletes the store with a given store_name; Returns the id of the deleted
    store.

    Keyword arguments:
    store_name -- the name of the store
    """
    # Check privlages of user attempting to delete store
    # Delete store
    # Return the status/output of the operation
    db = MongoClient()['store']
    store = db[store_name]
    store.drop()
    perms = db['permissions']
    perms.find_and_modify({"name": store_name}, remove=True)
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
