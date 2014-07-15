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
from common.shell import run_command


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
    (output, error, retcode) = run_command(gridutil.GLOBUS_CONF['LOCATION'] + "bin/globus-job-run %s /usr/common/usg/bin/qs -w" % (machine['hostname']), env=env)
    patt = re.compile(r'(?P<job_id>[^\s]+)\s+(?P<status>[^\s]+)\s+(?P<user>[^\s]+)\s+(?P<job_name>[^\s]+)\s+(?P<nodes>\d+)\s+(?P<walltime>[^\s]+)\s+(?P<time_use>[^\s]+)\s+(?P<time_submit>\w{3}\s\d{1,2}\s[\d\:]+)\s+(?P<rank>[^\s]+)\s+(?P<queue>[^\s]+)\s+(?P<q_state>[^\s]+)\s+(?P<processors>[^\s]+)\s+(?P<details>.*)$')

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
    pass


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
    (output, error, retcode) = run_command(gridutil.GLOBUS_CONF['LOCATION'] + "bin/globus-job-run %s /usr/common/usg/bin/qs -w %s" % (machine['hostname'], job_id), env=env)
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
    pass


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