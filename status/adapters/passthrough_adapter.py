# Passthrough Adapter
from django.conf import settings
import requests
from common.response import json_response
import logging
logger = logging.getLogger("newt." + __name__)

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

patterns = (
)

def extras_router(request, query):
    """Maps a query to a function if the pattern matches and returns result

    Keyword arguments:
    request -- Django HttpRequest
    query -- the query to be matched against
    """
    for pattern, func, req in patterns:
        match = pattern.match(query)
        if match and req:
            return func(request, **match.groupdict())
        elif match:
            return func(**match.groupdict())

    # Returns an Unimplemented response if no pattern matches
    return json_response(status="Unimplemented", 
                             status_code=501, 
                             error="", 
                             content="query: %s" % query)