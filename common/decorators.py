from common.response import json_response
from django.http import HttpRequest
import json
import inspect


def login_required(view_func):
    """
    Use this for class based views (i.e. first argument is self)
    """
    def wrapper(*args, **kwargs):
        # If view_func is a class view, args=[self, request, ... ]
        # If view_func is a regular function args=[request, ...]
        if isinstance(args[0], HttpRequest):
            request = args[0]
        elif isinstance(args[1], HttpRequest):
            request = args[1]
        else:
            return json_response(status="ERROR", 
                                 status_code=500, 
                                 error="Missing request object") 

        if request.user.is_authenticated():
            return view_func(*args, **kwargs)
        else:
            return json_response(status="ERROR", 
                                 status_code=403, 
                                 error="You must be logged in to access this.",
                                 content=json.dumps({"login_url": "/api/auth/"}))
    return wrapper


