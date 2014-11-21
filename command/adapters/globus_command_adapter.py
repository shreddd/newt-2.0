"""Command Adapter Template File

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
from common.decorators import login_required

@login_required
def execute(request, machine_name, command):
    """Returns a the result of running command on machine_name

    Keyword arguments:
    machine_name -- name of the machine
    command -- command to run
    """
    machine = gridutil.GRID_RESOURCE_TABLE.get(machine_name, None)
    if not machine:
        return json_response(status="ERROR", status_code=400, error="Invalid machine name: %s" % machine_name)
    
    # Get the grid credentials for the user
    env = gridutil.get_cred_env(request.user)
    try:
        # Run the command using globus-job-run
        (output, error, retcode) = run_command(gridutil.GLOBUS_CONF['LOCATION'] + "bin/globus-job-run %s %s" % (machine['hostname'], command), env=env)

        response = {
            "output": output,
            "error": error,
            "retcode": retcode
        }
        return response
    except Exception as e:
        logger.error("Could not run command: %s" % str(e))
        return json_response(error="Could not run command: %s" % str(e), status="ERROR", status_code=500)

@login_required
def get_systems(request):
    """Returns a list of all machines available to run commands on
    """
    systems = []
    for (machine, attr) in gridutil.GRID_RESOURCE_TABLE.iteritems():
        if 'fork' in attr['jobmanagers']:
            systems.append(machine)
    return systems


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