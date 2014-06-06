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
            "users": Users with access to the store (?)
        }

"""
from pymongo import MongoClient
def get_stores():
    """Returns a list of available stores"""
    db = MongoClient()['stores']
    return filter(lambda s: s!="system.indexes", db.collection_names())

def create_store(store_name, initial_data=[]):
    """Creates a store with the given store_name and initial_data

    Keyword arguments:
    store_name -- the name of the store
    initial_data -- initial data for the store (optional)
    """
    # Check that store name is unique (or create unique identifier)
    # Create new collection
    db = MongoClient()['stores']
    new_collection = db.create_collection(store_name)
    
    # Load initial data into the store
    oid_list = []
    for oid, data in enumerate(initial_data):
        new_collection.insert({"oid": str(oid), "data": data})
        oid_list.append(oid)
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
    return {"dropped": store_name}

def get_store_contents(store_name):
    """Returns a list containing all the contents of the store

    Keyword arguments:
    store_name -- the name of the store
    """
    # Check privlages of user attempting to access store
    if store_name not in get_stores():
        raise Exception('The store \"' + store_name + '\" does not exist.')
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
    return store.find_one({"name":store_name}, {"_id":0, "groups":1, "users":1})

def update_store_perms(store_name, perms):
    """Updates the permissions of the given store with perms

    Keyword arguments:
    store_name -- the name of the store
    perms -- dictionary of the updated permissions
    """
    # Updates the permissions of the store and returns the status
    pass

def store_insert(store_name, data):
    """Inserts data into the store

    Keyword arguments:
    store_name -- the name of the store
    data -- a list of key value pairs to be put in the store
    """
    # Insert the key value pairs into the store
    db = MongoClient()['stores']
    store = db[store_name]
    oid = str(store.count())
    store.insert({"oid": oid, "data": data})
    return {"id": oid}

def store_update(store_name, obj_id, data):
    """Updates a certain key-value pair in the store

    Keyword arguments:
    store_name -- the name of the store
    pair -- the updated pair (dict)
    """
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
        raise Exception("Invalid object id: " + obj_id)

