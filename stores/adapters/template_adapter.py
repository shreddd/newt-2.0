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
import re
logger = logging.getLogger("newt." + __name__)

def get_stores(request):
    """Returns a list of available store names.

    Keyword arguments:
    request -- Django HttpRequest object
    """
    pass

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
    pass

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
   pass

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
    pass

def store_get_obj(request, store_name, obj_id):
    """Returns the data of the specified document in the store.

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    obj_id -- ID of the object in the store
    """
    pass

def store_insert(request, store_name, initial_data):
    """Creates a new document in the store with initial_data; Returns the oid 
    of the new document.

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    initial_data -- document data
    """
    pass

def store_update(request, store_name, obj_id, data):
    """Updates the contents of a given document; Returns the oid of the 
    document.

    Keyword arguments:
    request -- Django HttpRequest object
    store_name -- the name of the store
    obj_id -- ID of the document in the store
    data -- Updated data of the document
    """
    pass

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
    pass

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
    pass

def delete_store(request, store_name):
    """Deletes the store with a given store_name; Returns the id of the deleted
    store.

    Keyword arguments:
    store_name -- the name of the store
    """
    pass

"""A tuple list in the form of:
    (
        (compiled_regex_exp, associated_function, request_required),
        ...
    )

    Note: The compiled_regex_exp must have named groups corresponding to
          the arguments of the associated_function
    Note: if request_required is True, the associated_function must have
          request as the first argument

    Example:
        patterns = (
            (re.compile(r'/usage/(?P<path>.+)$'), get_usage, False),
            (re.compile(r'/image/(?P<query>.+)$'), get_image, False),
            (re.compile(r'/(?P<path>.+)$'), get_resource, False),
        )
"""
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