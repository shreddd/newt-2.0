import requests
from django.conf import settings
from django.http import Http404, HttpResponseServerError, HttpResponse
from common.response import json_response

nim_base_url = settings.NEWT_CONFIG['NIM_BASE_URL']

def get_user_info(user_name=None, uid=None):
    if uid:
        return get_resource("user/id/%d/" % uid)
    elif user_name:
        return get_resource("user/%s/" % user_name)
    else:
        return json_response(status=ERROR, 
                             status_code=400, 
                             error="No data received.")

def get_group_info(group_name=None, gid=None):
    if gid:
        return get_resource("group/id/%d/" % uid)
    elif group_name:
        return get_resource("user/%s/" % user_name)
    else:
        return json_response(status=ERROR, 
                             status_code=400, 
                             error="No data received.")
def get_resource(path):
    r = requests.get(nim_base_url + "/info/json/" + path)
    if r.status_code == 200:
        return r.json()['items']
    else:
        return json_response(status="ERROR", 
                             status_code=500, 
                             error="Invalid resource location: " + path)

def get_usage(path):
    r = requests.get(nim_base_url + "/usage/" + path + "/json/")
    if r.status_code == 200:
        return r.json()['items']
    else:
        return json_response(status="ERROR", 
                             status_code=500, 
                             error="Invalid resource location: " + path)

def get_image(query):
    import re
    r = requests.get(nim_base_url + "/info/json/image/" + query)
    if r.status_code == 200:
        if re.search(r'\/photo\/?$', query):
            return HttpResponse(r.content, content_type=r.headers['content-type'])
        return r.json()['items']
    elif r.status_code == 404:
        return json_response(status="ERROR", 
                             status_code=404, 
                             error="Image not found at: " + path)
    else:
        return json_response(status="ERROR", 
                             status_code=500, 
                             error="Invalid image location: " + query)

import re
patterns = (
    (re.compile(r'/usage/(?P<path>.+)$'), get_usage, False),
    (re.compile(r'/image/(?P<query>.+)$'), get_image, False),
    (re.compile(r'/(?P<path>.+)$'), get_resource, False),
)

def extras_router(request, query):
    for pattern, func, req in patterns:
        match = pattern.match(query)
        if match and req:
            return func(request, **match.groupdict())
        elif match:
            return func(**match.groupdict())

    return json_response(status="Unimplemented", 
                             status_code=501, 
                             error="", 
                             content="query: %s" % query)
