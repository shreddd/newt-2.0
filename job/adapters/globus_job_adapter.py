"""Job Adapter Template File

IMPORTANT: NOT A FUNCTIONAL ADAPTER. FUNCTIONS MUST BE IMPLEMENTED

Notes:
    - Each of the functions defined below must return a json serializable
      object, json_response, or valid HttpResponse object
    - A json_response creates an HttpResponse object given parameters:
        - content: string with the contents of the response 
        - status: string with the status of the response 
        - status_code: HTTP status code 
        - error: string with the error message if there is one 
"""
from common.response import json_response
import logging
import re
logger = logging.getLogger("newt." + __name__)
from common import gridutil
from common.gridutil import GlobusHelper
from common.shell import run_command
import tempfile


def get_machines(request):
    """Returns the available machines that jobs can run on

    Keyword arguments:
    request - Django HttpRequest
    """
    machines = {}
    for (machine, attrs) in gridutil.GRID_RESOURCE_TABLE.iteritems():
        if attrs['jobmanagers'] != {}:
            machines[machine] = attrs['jobmanagers']
    return machines


def view_queue(request, machine_name):
    """Returns the current state of the queue in a list

    Keyword arguments:
    request -- Django HttpRequest
    machine_name -- name of the machine
    """
    machine = gridutil.GRID_RESOURCE_TABLE.get(machine_name, None)
    if not machine:
        return json_response(status="ERROR", status_code=400, error="Invalid machine name: %s" % machine_name)

    env = gridutil.get_cred_env(request.user)
    (output, error, retcode) = run_command(gridutil.GLOBUS_CONF['LOCATION'] + "bin/globus-job-run %s /project/projectdirs/osp/newt_tools/qs_moab.sh" % (machine['hostname']), env=env)
    patt = re.compile(r'(?P<job_id>[^\s]+)\s+(?P<status>[^\s]+)\s+(?P<user>[^\s]+)\s+(?P<job_name>[^\s]+)\s+(?P<nodes>\d+)\s+(?P<walltime>[^\s]+)\s+(?P<time_use>[^\s]+)\s+(?P<time_submit>\w{3}\s\d{1,2}\s[\d\:]+)\s+(?P<rank>[^\s]+)\s+(?P<queue>[^\s]+)\s+(?P<q_state>[^\s]+)\s+(?P<processors>[^\s]+)\s*(?P<details>.*)$')

    if retcode != 0:
        return json_response(status="ERROR", status_code=500, error="Unable to get queue: %s" % error)
    # filter out stuff that doesn't match pattern
    output = output.splitlines()
    output = [x.strip() for x in output]
    output = filter(lambda line: patt.match(line), output)

    # Convert output into dict from group names
    output = map(lambda x: patt.match(x).groupdict(), output)

    return output


def submit_job(request, machine_name):
    """Submits a job to the queue

    Keyword arguments:
    request -- Django HttpRequest
    machine_name -- name of the machine
    """
    machine = gridutil.GRID_RESOURCE_TABLE.get(machine_name, None)
    if not machine:
        return json_response(status="ERROR", status_code=400, error="Invalid machine name: %s" % machine_name)

    flags = ""
    jobmanager = machine['jobmanagers']['fork']['url']
    qsub = machine['qsub']['bin']
    scheduler = machine['qsub']['scheduler']

    # Set environment flags for qsub
    if scheduler == "sge":
        sge_env_str = "-env SGE_ROOT=%s -env SGE_QMASTER_PORT=%s -env SGE_EXECD_PORT=%s" % (gridutil.SGE_ROOT, gridutil.SGE_QMASTER_PORT, gridutil.SGE_EXECD_PORT)
        flags += " " + sge_env_str

    if request.POST.get("jobfile", False):
        # Create command for qsub on an existing pbs file
        job_file_path = request.POST.get("jobfile")
        cmd = "%s %s" % (qsub, job_file_path)
    elif request.POST.get("jobscript", False):
        # Create command for qsub from stdin data
        job_script = request.POST.get("jobscript")

        # Creates a temporary job file
        tmp_job_file = tempfile.NamedTemporaryFile(prefix="newt_")
        tmp_job_file.write(job_script)
        tmp_job_file.flush()

        # Stages the temporary job file and pass it as to stdin to qsub
        flags += " -stdin -s %s" % tmp_job_file.name
        cmd = qsub
    else:
        return json_response(status="ERROR", 
                             status_code=400, 
                             error="No data received")

    if scheduler != "sge":
        cmd = '/bin/bash -l -c "%s"' % cmd

    try:
        runner = GlobusHelper(request.user)
        (output, error, retcode) = runner.run_job(cmd, jobmanager, flags)
    except Exception, ex:
        return json_response(status="ERROR", 
                             status_code=500, 
                             error="qsub failed with error: %s" % str(ex))
    if retcode != 0:
        return json_response(status="ERROR", 
                             status_code=500, 
                             error="qsub failed with error: %s" % error)
    return {"jobid":output.strip()}


def get_info(request, machine_name, job_id):
    """Gets the information of a job, given the id

    Keyword arguments:
    machine_name -- name of the machine
    job_id -- the job id
    """
    machine = gridutil.GRID_RESOURCE_TABLE.get(machine_name, None)
    if not machine:
        return json_response(status="ERROR", status_code=400, error="Invalid machine name: %s" % machine_name)

    env = gridutil.get_cred_env(request.user)
    (output, error, retcode) = run_command(gridutil.GLOBUS_CONF['LOCATION'] + "bin/globus-job-run %s /project/projectdirs/osp/newt_tools/qs_moab.sh %s" % (machine['hostname'], job_id), env=env)
    patt = re.compile(r'(?P<job_id>[^\s]+)\s+(?P<status>[^\s]+)\s+(?P<user>[^\s]+)\s+(?P<job_name>[^\s]+)\s+(?P<nodes>\d+)\s+(?P<walltime>[^\s]+)\s+(?P<time_use>[^\s]+)\s+(?P<time_submit>\w{3}\s\d{1,2}\s[\d\:]+)\s+(?P<rank>[^\s]+)\s+(?P<queue>[^\s]+)\s+(?P<q_state>[^\s]+)\s+(?P<processors>[^\s]+)\s*(?P<details>.*)$')

    if retcode != 0:
        return json_response(status="ERROR", status_code=500, error="Unable to get queue: %s" % error)
    # filter out stuff that doesn't match pattern
    output = output.splitlines()
    output = [x.strip() for x in output]
    output = filter(lambda line: patt.match(line), output)

    # Convert output into dict from group names
    output = map(lambda x: patt.match(x).groupdict(), output)[0]

    return output


def delete_job(request, machine_name, job_id):
    """Gets the information of a job, given the id

    Keyword arguments:
    machine_name -- name of the machine
    job_id -- the job id
    """
    machine = gridutil.GRID_RESOURCE_TABLE.get(machine_name, None)
    if not machine:
        return json_response(status="ERROR", status_code=400, error="Invalid machine name: %s" % machine_name)

    flags = ""
    jobmanager = machine['jobmanagers']['fork']['url']
    qdel = machine['qdel']['bin']
    scheduler = machine['qdel']['scheduler']
    cmd = "%s %s" % (qdel, job_id)

    # Set environment flags for qsub
    if scheduler == "sge":
        sge_env_str = "-env SGE_ROOT=%s -env SGE_QMASTER_PORT=%s -env SGE_EXECD_PORT=%s" % (gridutil.SGE_ROOT, gridutil.SGE_QMASTER_PORT, gridutil.SGE_EXECD_PORT)
        flags += " " + sge_env_str

    if scheduler != "sge":
        cmd = '/bin/bash -l -c "%s"' % cmd

    try:
        runner = GlobusHelper(request.user)
        (output, error, retcode) = runner.run_job(cmd, jobmanagers, flags)
    except Exception, ex:
        return json_response(status="ERROR", 
                             status_code=500, 
                             error="qsub failed with error: %s" % str(ex))
    if retcode != 0:
        return json_response(status="ERROR", 
                             status_code=500, 
                             error="qsub failed with error: %s" % error)
    return output


"""A tuple list in the form of:
    (
        (compiled_regex_exp, associated_function, request_required),
        ...
    )

    Note: The compiled_regex_exp must have named groups corresponding to
          the arguments of the associated_function
    Note: if request_required is True, the associated_function must have
          request as the first argument

    Example:
        patterns = (
            (re.compile(r'/usage/(?P<path>.+)$'), get_usage, False),
            (re.compile(r'/image/(?P<query>.+)$'), get_image, False),
            (re.compile(r'/(?P<path>.+)$'), get_resource, False),
        )
"""
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