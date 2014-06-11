import requests
from django.conf import settings
from django.http import Http404, HttpResponseServerError, HttpResponse
from common.response import json_response

nim_base_url = settings.NEWT_CONFIG['NIM_BASE_URL']

def get_resource(path):
    r = requests.get(nim_base_url + "/info/json/" + path)
    if r.status_code == 200:
        return r.json()['items']
    else:
        return json_response(status="ERROR", status_code=500, error="Invalid resource location: " + path)

def get_usage(path):
    r = requests.get(nim_base_url + "/usage/" + path + "/json/")
    if r.status_code == 200:
        return r.json()['items']
    else:
        return json_response(status="ERROR", status_code=500, error="Invalid resource location: " + path)

def get_image(query):
    import re
    r = requests.get(nim_base_url + "/info/json/image/" + query)
    if r.status_code == 200:
        if re.search(r'\/photo\/?$', query):
            return HttpResponse(r.content, content_type=r.headers['content-type'])
        return r.json()['items']
    elif r.status_code == 404:
        return json_response(status="ERROR", status_code=404, error="Image not found at: " + path)
    else:
        return json_response(status="ERROR", status_code=500, error="Invalid image location: " + query)

