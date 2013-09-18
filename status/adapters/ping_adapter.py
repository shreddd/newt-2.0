# Ping Status Adapter
from django.conf import settings
import os


def ping(machine_name, hostname):
    # Do a single ping with timeout 2 seconds
    retcode = os.system('ping -c1 -t2 %s' % hostname)
    if retcode == 0:
        return {'system': machine_name, 'status': 'up'}
    else:
        return {'system': machine_name, 'status': 'down'}



def get(machine_name=None):
    conf = settings.NEWT_CONFIG

    if machine_name == None:
        return [ ping(s['NAME'], s['HOSTNAME']) for s in conf['SYSTEMS'] ] 
            
    else: 
        hostname = None
        for s in conf.SYSTEMS:
            if machine_name==s['NAME']:
                hostname = machine_name['HOSTNAME']
                break

        if hostname is None:
            raise ValueError("unrecognized system %s" % machine_name)

        return ping(machine_name, hostname)

