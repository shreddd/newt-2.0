from common.response import json_response
import logging
logger = logging.getLogger(__name__)
from common.shell import run_command
import re
from bson.objectid import ObjectId
from subprocess import Popen, PIPE
from django.conf import settings
from datetime import datetime
import pytz

def get_queues():
    """Returns the available queues that jobs can run on

    Keyword arguments:
    request - Django HttpRequest
    """
    return ['localhost']


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
    # Get data from POST
    if request.POST.get("jobfile", False):
        try:
            f = open(request.POST.get("jobfile"), 'r')
            data = f.read()
        except Exception as e:
            return json_response(status="ERROR", 
                                 status_code=400, 
                                 error="Unable to open job file. Be sure you gave an absolute path.")
        finally:
            f.close()
    elif request.POST.get("jobscript", False):
        data = request.POST.get("jobscript")
    else:
        return json_response(status="ERROR", 
                             status_code=400, 
                             error="No data received")

    # Generate unique outfile name
    tmp_job_name = str(ObjectId()) + ".out"

    # Get job emulator path
    job_emu = settings.PROJECT_DIR + "/job/adapters/emulate_job_run.sh"

    # Run job with the commands in data
    job = Popen([job_emu, tmp_job_name, request.user.username, data], stdout=PIPE)

    # Get/return the job_id from stdout
    job_id = job.stdout.readline().rstrip()
    return {"jobid": job_id}    


def get_info(machine_name, job_id):
    """Gets the information of a job, given the id

    Keyword arguments:
    machine_name -- name of the machine
    job_id -- the job id
    """
    try:
        job_out = open("/tmp/newt_processes/%s.log" % job_id, 'r')
        lines = job_out.read().splitlines()
        job_out.close()
    except Exception as e:
        return {
            "jobid": job_id,
            "user": "",
            "status": "queue",
            "time_start": "",
            "time_end": "",
            "time_used": "",
            "output": ""
        }
    output = "\n".join(lines[1:])
    info = lines[0].split("; ")
    time_start = datetime.fromtimestamp(float(info[3]), tz=pytz.timezone("utc"))
    time_end = "" if info[2] == "999" else datetime.fromtimestamp(float(info[4]), tz=pytz.timezone("utc"))
    if info[2] == "999":
        time_used = datetime.utcnow().replace(tzinfo=pytz.timezone(("utc"))) - time_start
    else:
        time_used = time_end - time_start
    info = {
        "jobid": info[0],
        "user": info[1],
        "status": "running" if info[2] == "999" else info[2],
        "time_start": str(time_start),
        "time_end": str(time_end),
        "time_used": str(time_used),
        "output": output
    }
    return info    


def delete_job(machine_name, job_id):
    """Gets the information of a job, given the id

    Keyword arguments:
    machine_name -- name of the machine
    job_id -- the job id
    """
    (output, error, retcode) = run_command("kill %s" % job_id)
    if retcode != 0:
        return json_response(status="ERROR",
                             status_code=500,
                             error=error)
    return {"output": output}