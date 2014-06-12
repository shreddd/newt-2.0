"""Status Adapter Template File

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

def get_status(machine_name=None):
    """ Returns the status of a given machine (if machine_name is set),
        otherwise the statuses of all the machines

    Keyword arguments
    machine_name -- (optional) name of the machine
    """
    pass