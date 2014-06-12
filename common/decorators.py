from common.response import json_response
import json


def login_required(view_func):
    def wrapper(*args, **kwargs):
        request = args[1]
        if request.user.is_authenticated():
            return view_func(*args, **kwargs)
        else:
            return json_response(status="ERROR", 
                                 status_code=403, 
                                 error="You must be logged in to access this.",
                                 content=json.dumps({"login_url": "/api/auth/"}))
    return wrapper