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

def get_stores():
    """Returns a list of available stores"""
    stores = [store.name for store in Store.objects.all()]
    return stores

def create_store(request, store_name):
    """Creates a store with the given store_name and initial_data

    Keyword arguments:
    request -- request the data can be derived from
    store_name -- the name of the store
    """
    if not store_name:
        store_name = random.choice(string.ascii_letters) + str(uuid.uuid4())[0:8]
        while(store_name in get_stores()):
            store_name = str(uuid.uuid4())[0:8]
    elif Store.objects.filter(name=store_name).count() > 0:
        return json_response(status="ERROR", status_code=400, error="Store name already exists: %s" % store_name)
    store = Store(name=store_name)
    store.save()
    if request.user.pk is not None:
        u = User.objects.get(pk=request.user.pk)
        perm = Permission(user=u, store=store, type="rw")
        perm.save()
    # Load initial data
    initial_data = json.loads(request.POST.get("data", "[]"))
    oid_list = []
    for oid, data in enumerate(initial_data):
        new_doc = Document(oid=int(oid), data=data, store=store)
        new_doc.save()
        oid_list.append(oid)

    return {"id": store.name, "oid": oid_list}

def delete_store(store_name):
    """Deletes the store with a given store_name

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

    return {"dropped": store_name}

def get_store_contents(store_name):
    """Returns a list containing all the contents of the store

    Keyword arguments:
    store_name -- the name of the store
    """
    try:
        store = Store.objects.get(name=store_name)
    except ObjectDoesNotExist:
        return json_response(status="ERROR", 
                             status_code=404, 
                             error="Store does not exist: %s" % store_name)
    documents = [doc.data for doc in store.documents.all()]
    return documents

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
            "perms": [p for p in perm.type],
        })

    info = {
        "name": store_name,
        "users": perm_list,
    }
    return info


def update_store_perms(request, store_name):
    """Updates the permissions of the given store with perms

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
    perms = request.POST.get("data", None)
    if not perms:
        return json_response(status="ERROR", status_code=400, error="No data received.")
    for new_perm in json.loads(perms):
        try:
            perm = Permission.objects.get(user__username=new_perm['name'], store=store)
        except ObjectDoesNotExist:
            u = User.objects.get(username=new_perm['name'])
            perm = Permission(store=store, user=u)
        perm.type = "".join(new_perm['perms'])
        perm.save()

    return {"id": store_name}

def store_insert(request, store_name):
    """Inserts data into the store

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
    data = request.POST.get("data", None)
    if not data:
        return json_response(status="ERROR", status_code=400, error="No data received.")
    oid = store.documents.count()
    new_doc = Document(oid=oid, data=data, store=store)
    new_doc.save()

    return {"id": str(oid)}

def store_update(request, store_name, obj_id):
    """Updates a certain key-value pair in the store

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
    data = json.loads(request.body).get("data", None)
    if not data:
        return json_response(status="ERROR", status_code=400, error="No data received.")
    doc = store.documents.get(oid=obj_id)
    doc.data = data
    doc.save()

    return {"data": data}

def store_get_obj(store_name, obj_id):
    """Gets the value of the specified key in the store 

    Keyword arguments:
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

