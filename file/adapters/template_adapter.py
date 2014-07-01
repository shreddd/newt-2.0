"""File Adapter Template File

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
from django.http import StreamingHttpResponse
from common.response import json_response
import logging
import re
logger = logging.getLogger(__name__)


def download_path(request, machine_name, path):
    """Returns a StreamingHttpResponse with the file

    Keyword arguments:
    machine_name -- name of the machine
    path -- path to file
    """
    pass


def put_file(request, machine, path):
    """Writes the uploaded file to path and returns the path

    Keyword arguments:
    request -- HttpRequest containing the data
    machine_name -- name of the machine
    path -- path to file
    """
    pass
    
    
def get_dir(request, machine_name, path):
    """Returns a directory listing of path (as an array)

    Keyword arguments:
    machine_name -- name of the machine
    path -- path to file
    """
    pass


def get_systems(request):
    """Returns a list of all the systems available
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