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
     