# Passthrough Adapter
from django.conf import settings
import requests

def get(machine_name=None):
    base_url = settings.STATUS_URL
    if machine_name==None:
        url = base_url
    else:
        url = '%s?%s=%s' % (base_url, 'system', machine_name)
    
    r = requests.get(url)
    data = r.json()
    if data['status'] == "unknown":
        return json_response(status="ERROR", 
                             status_code=400, 
                             error="Unrecognized system: %s" % machine_name))
    return data

