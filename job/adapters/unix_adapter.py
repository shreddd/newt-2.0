from common.response import json_response
import logging
logger = logging.getLogger(__name__)
from common.shell import run_command
import re


def view_queue(request, machine_name):
    """Returns the current state of the queue in a list

    Keyword arguments:
    request -- Django HttpRequest
    machine_name -- name of the machine
    """
    (output, error, retcode) = run_command("ps -aj")
    patt = re.compile(r'(?P<user>[^\s]+)\s+(?P<jobid>\d+)\s+(?P<ppid>\d+)\s+(?P<pgid>\d+)\s+(?P<sess>\d+)\s+(?P<jobc>\d+)\s+(?P<status>[^\s]+)\s+(?P<tt>[^\s]+)\s+(?P<timeuse>[^\s]+)\s+(?P<command>.+)')
    processes = output.splitlines()[1:]
    processes = map(lambda x: patt.match(x).groupdict(), processes)
    return processes


def submit_job(request, machine_name):
    """Submits a job to the queue

    Keyword arguments:
    request -- Django HttpRequest
    machine_name -- name of the machine
    """
    pass


def get_info(machine_name, job_id):
    """Gets the information of a job, given the id

    Keyword arguments:
    machine_name -- name of the machine
    job_id -- the job id
    """
    (output, error, retcode) = run_command("ps aux %d" % job_id)
    patt = re.compile(r'(?P<user>[^\s]+)\s+(?P<jobid>\d+)\s+(?P<cpu>[\d\.]+)\s+(?P<mem>[\d\.]+)\s+(?P<vsz>\d+)\s+(?P<rss>\d+)\s+(?P<tt>[^\s]+)\s+(?P<stat>[^\s]+)\s+(?P<started>[^\s]+)\s+(?P<timeuse>[^\s]+)\s+(?P<command>.+)')
    info = patt.match(output.splitlines()[1]).groupdict()
    return info    


def delete_job(machine_name, job_id):
    """Gets the information of a job, given the id

    Keyword arguments:
    machine_name -- name of the machine
    job_id -- the job id
    """
    (output, error, retcode) = run_command("kill %d" % job_id)
    if retcode != 0:
        return json_response(status="ERROR",
                             status_code=500,
                             error=error)
    return {"output": output}