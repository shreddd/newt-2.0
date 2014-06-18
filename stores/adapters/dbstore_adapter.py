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

import json
from dbstore_models import *
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import uuid, random, string

def get_stores(request):
    """Returns a list of available store names.

    Keyword arguments:
    request -- Django HttpRequest object
    """
    stores = [store.name for store in Store.objects.all()]
    return stores

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
    if not store_name:
        store_name = random.choice(string.ascii_letters) + str(uuid.uuid4())[0:8]
        while(store_name in get_stores(request)):
            store_name = str(uuid.uuid4())[0:8]
    elif Store.objects.filter(name=store_name).count() > 0:
        return json_response(status="ERROR", status_code=400, error="Store name already exists: %s" % store_name)
    store = Store(name=store_name)
    store.save()
    if request.user.pk is not None:
        u = User.objects.get(pk=request.user.pk)
        perm = Permission(user=u, store=store, type="r,w")
        perm.save()
    # Load initial data
    oid_list = []
    for oid, data in enumerate(initial_data):
        new_doc = Document(oid=int(oid), data=data, store=store)
        new_doc.save()
        oid_list.append(str(oid))

    return {"id": store.name, "oid": oid_list}

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
    try:
        store = Store.objects.get(name=store_name)
    except ObjectDoesNotExist:
        return json_response(status="ERROR", 
                             status_code=404, 
                             error="Store does not exist: %s" % store_name)
    documents = [{"oid": str(doc.oid), "data": doc.data} for doc in store.documents.all()]
    return documents

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
    try:
        store = Store.objects.get(name=store_name)
    except ObjectDoesNotExist:
        return json_response(status="ERROR", 
                             status_code=404, 
                             error="Store does not exist: %s" % store_name)
    doc = store.documents.get(oid=obj_id)
    return doc.data

def store_insert(request, store_name, initial_data):
    """Creates a new document in the store with initial_data; Returns the oid 
    of the new document.

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    initial_data -- document data
    """
    try:
        store = Store.objects.get(name=store_name)
    except ObjectDoesNotExist:
        return json_response(status="ERROR", 
                             status_code=404, 
                             error="Store does not exist: %s" % store_name)
    data = initial_data
    if not data:
        return json_response(status="ERROR", status_code=400, error="No data received.")
    oid = store.documents.count()
    new_doc = Document(oid=oid, data=data, store=store)
    new_doc.save()

    return str(oid)

def store_update(request, store_name, obj_id, data):
    """Updates the contents of a given document; Returns the oid of the 
    document.

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    obj_id -- ID of the document in the store
    data -- Updated data of the document
    """
    try:
        store = Store.objects.get(name=store_name)
    except ObjectDoesNotExist:
        return json_response(status="ERROR", 
                             status_code=404, 
                             error="Store does not exist: %s" % store_name)
    if not data:
        return json_response(status="ERROR", status_code=400, error="No data received.")
    doc = store.documents.get(oid=obj_id)
    doc.data = data
    doc.save()

    return str(doc.oid)

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
    try:
        store = Store.objects.get(name=store_name)
    except ObjectDoesNotExist:
        return json_response(status="ERROR", 
                             status_code=404, 
                             error="Store does not exist: %s" % store_name)
    perms = store.perms.all()
    perm_list = []
    for perm in perms:
        perm_list.append({
            "name": perm.user.username,
            "perms": perm.type.split(","),
        })

    info = {
        "name": store_name,
        "perms": perm_list,
    }
    return info


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
    try:
        store = Store.objects.get(name=store_name)
    except ObjectDoesNotExist:
        return json_response(status="ERROR", 
                             status_code=404, 
                             error="Store does not exist: %s" % store_name)
    for new_perm in perms:
        try:
            perm = Permission.objects.get(user__username=new_perm['name'], store=store)
        except ObjectDoesNotExist:
            u = User.objects.get(username=new_perm['name'])
            perm = Permission(store=store, user=u)
        perm.type = ",".join(new_perm['perms'])
        perm.save()

    return store_name

def delete_store(request, store_name):
    """Deletes the store with a given store_name; Returns the id of the deleted
    store.

    Keyword arguments:
    store_name -- the name of the store
    """
    try:
        store = Store.objects.get(name=store_name)
        store.delete()
    except ObjectDoesNotExist:
        return json_response(status="ERROR", 
                             status_code=404, 
                             error="Store does not exist: %s" % store_name)
    except MultipleObjectsReturned:
        logger.warn("Multiple stores with the same name found.")
        stores = Store.objects.filter(name=store_name)
        stores.delete()

    return store_name

