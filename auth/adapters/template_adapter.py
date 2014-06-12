"""Auth Adapter Template File

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


def get_status(request):
    """Returns the current user status

    Keyword arguments:
    request -- Django HttpRequest
    """
    pass


def login(request):
    """Logs the user in and returns the status

    Keyword arguments:
    request -- Django HttpRequest
    """
    pass


def logout(request):
    """Logs the user out and returns the status

    Keyword arguments:
    request -- Django HttpRequest
    """
    pass