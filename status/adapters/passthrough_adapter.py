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
    
    return r.json()

