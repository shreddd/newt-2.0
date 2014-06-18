# Ping Status Adapter
from django.conf import settings
import os
from common.shell import run_command
from common.response import json_response
import logging
logger = logging.getLogger(__name__)


def ping(machine_name, hostname):
    # Do a single ping with timeout 2 seconds
    (output, err, retcode) = run_command('ping -c1 -t2 %s' % hostname)
    if retcode == 0:
        return {'system': machine_name, 'status': 'up'}
    else:
        return {'system': machine_name, 'status': 'down'}

def get_status(machine_name=None):
    """ Returns the status of a given machine (if machine_name is set),
        otherwise the statuses of all the machines

    Keyword arguments
    machine_name -- (optional) name of the machine
    """
    conf = settings.NEWT_CONFIG

    if machine_name == None:
        return [ ping(s['NAME'], s['HOSTNAME']) for s in conf['SYSTEMS'] ] 
            
    else: 
        hostname = None
        for s in conf['SYSTEMS']:
            if machine_name==s['NAME']:
                hostname = s['HOSTNAME']
                break

        if hostname is None:
            return json_response(status="ERROR", 
                                 status_code=404, 
                                 error="Unrecognized system: %s" % machine_name)
        return ping(machine_name, hostname)

