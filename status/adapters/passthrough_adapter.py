# Passthrough Adapter
from django.conf import settings
import requests
from common.response import json_response
import logging
logger = logging.getLogger(__name__)

def get_status(machine_name=None):
    """ Returns the status of a given machine (if machine_name is set),
        otherwise the statuses of all the machines

    Keyword arguments
    machine_name -- (optional) name of the machine
    """
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

