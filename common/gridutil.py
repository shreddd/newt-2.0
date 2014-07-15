import shlex
import os
import urllib
import re
from auth.models import Cred
import logging
logger = logging.getLogger("newt." + __name__)

GRID_RESOURCE_TABLE = dict(
    genepool=dict(
        hostname='genepool01.nersc.gov', 
        jobmanagers=dict(fork=dict(url="genepool01.nersc.gov/jobmanager"), 
                         batch=dict(url="genepool01.nersc.gov/jobmanager-sge")),
        gridftp_servers=['genepool01.nersc.gov'],
        qstat=dict(bin='/project/projectdirs/osp/newt_tools/qstat_sge.sh', scheduler='sge'),
        qsub=dict(bin='/opt/uge/genepool/uge/bin/lx-amd64/qsub', scheduler='sge'),
        qdel=dict(bin='/opt/uge/genepool/uge/bin/lx-amd64/qdel', scheduler='sge'),
    ),
    edison=dict(
        hostname='edisongrid.nersc.gov', 
        jobmanagers=dict(fork=dict(url="edisongrid.nersc.gov/jobmanager"), 
                         batch=dict()),
        gridftp_servers=['edisongrid.nersc.gov'],
        qstat=dict(bin='/project/projectdirs/osp/newt_tools/qs_moab.sh',scheduler='qs'),
        qsub=dict(bin='/opt/torque/4.1.4/bin/qsub',scheduler='pbs'),
        qdel=dict(bin='/opt/torque/4.1.4/bin/qdel',scheduler='pbs'),
    ),        
    pdsf=dict(
        hostname='pdsfgrid2.nersc.gov', 
        jobmanagers=dict(fork=dict(url="pdsfgrid2.nersc.gov/jobmanager"), 
                         batch=dict(url="pdsfgrid2.nersc.gov/jobmanager-sge")),
        gridftp_servers=['pdsfgrid.nersc.gov'],
        qstat=dict(bin='/project/projectdirs/osp/newt_tools/qstat_sge.sh',scheduler='sge'),
        qsub=dict(bin='/common/nsg/sge/ge-8.1.2/bin/lx-amd64/qsub',scheduler='sge'),
        qdel=dict(bin='/common/nsg/sge/ge-8.1.2/bin/lx-amd64/qsub',scheduler='sge'),
    ),
    hopper=dict(
        hostname='hoppergrid.nersc.gov', 
        jobmanagers=dict(fork=dict(url="hoppergrid.nersc.gov/jobmanager"), 
                         batch=dict(url="hoppergrid.nersc.gov/jobmanager-pbs")),
        gridftp_servers=['hoppergrid.nersc.gov'],
        # qstat=dict(bin='/usr/common/nsg/bin/qstat',scheduler='pbs'),        
        qstat=dict(bin='/project/projectdirs/osp/newt_tools/qs_moab.sh',scheduler='qs'),
        qsub=dict(bin='/opt/torque/default/bin/qsub',scheduler='pbs'),        
        qdel=dict(bin='/opt/torque/default/bin/qdel',scheduler='pbs'),                                            
    ),
    carver=dict(
        hostname='carvergrid.nersc.gov', 
        jobmanagers=dict(fork=dict(url="carvergrid.nersc.gov/jobmanager"), 
                         batch=dict(url="carvergrid.nersc.gov/jobmanager-pbs")),
        gridftp_servers=['carvergrid.nersc.gov'],
        # qstat=dict(bin='/usr/syscom/opt/torque/default/bin/qstat',scheduler='pbs'),        
        qstat=dict(bin='/project/projectdirs/osp/newt_tools/qs_moab.sh',scheduler='qs'),
        qsub=dict(bin='/usr/syscom/opt/torque/default/bin/qsub',scheduler='pbs'),        
        qdel=dict(bin='/usr/syscom/opt/torque/default/bin/qdel',scheduler='pbs'),        
    ),
    datatran=dict(
        hostname='dtn01.nersc.gov', 
        jobmanagers=dict(),
        gridftp_servers=['dtn01.nersc.gov','dtn02.nersc.gov'],
        qstat=dict(),
    ),
    archive=dict(
        hostname='garchive.nersc.gov', 
        jobmanagers=dict(),
        gridftp_servers=['garchive.nersc.gov'],
        qstat=dict(),
    )
)

MYPROXY_CONFIG = dict(
    SERVER="nerscca2.nersc.gov",
    PATH="/global/scratch2/sd/tsun/",
    PREFIX="newt_x509up_u",
)

GLOBUS_CONF = {
    "LOCATION": "/global/common/datatran/dsg/globus-5.0.4/",
    "TCP_PORT_RANGE": "60000,65000",
    "HOSTNAME": "newt.nersc.gov",
    "LIB_PATH": "/global/common/datatran/dsg/globus-5.0.4/lib/"
}

def is_sanitized(input):
    return not re.search(r'[^ a-zA-Z0-9!@#%^_+:./-]', input)

def get_cred_env(user):
    """Creates a cert file for the user and returns the environment

    Keyword arguments:
    user -- django.contrib.auth.model.user object
    """
    def create_cert(path, data):
        logger.debug("Creating x509 cert in directory: %s" % path)
        oldmask=os.umask(077)
        f = file(path,'w')
        f.write(data)
        f.close()
        os.umask(oldmask)

    try:
        cred = Cred.objects.filter(user=user)[0]
    except IndexError:
        logger.error("No credentials found for user: %s" % user.username)
        raise Exception("No credentials found for user: %s" % user.username)

    cred_path = '%s/%s%s' % (MYPROXY_CONFIG['PATH'], 
                             MYPROXY_CONFIG['PREFIX'], 
                             user.username)
    create_cert(cred_path, cred.cert + cred.key + cred.calist)

    env = os.environ.copy()
    env['X509_USER_PROXY'] = cred_path
    env['GLOBUS_LOCATION'] = GLOBUS_CONF['LOCATION']
    env['GLOBUS_TCP_PORT_RANGE'] = GLOBUS_CONF['TCP_PORT_RANGE']
    env['GLOBUS_HOSTNAME'] = GLOBUS_CONF['HOSTNAME']

    if env.has_key('LD_LIBRARY_PATH'):        
        env['LD_LIBRARY_PATH'] = GLOBUS_CONF['LIB_PATH'] + ":" + env['LD_LIBRARY_PATH']
    else:
        env['LD_LIBRARY_PATH'] = GLOBUS_CONF['LIB_PATH']

    return env

def get_grid_path(machine, path):
    hostname = GRID_RESOURCE_TABLE[machine].get('hostname', machine)
    path = urllib.unquote(path)
    path = urllib.pathname2url(path)
    if not is_sanitized(path):
        raise ValueError("Bad Pathname")
    return "gsiftp://" + hostname + "/" + path