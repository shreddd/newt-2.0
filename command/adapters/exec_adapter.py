from common.shell import run_command
from common.response import json_response
import logging
logger = logging.getLogger(__name__)


def execute(machine_name, command):
    try:
        (output, error, retcode) = run_command(command)
        response = {
            'stdout': output,
            'stderr': error,
            'retcode': retcode
        }
        return response
    except Exception as e:
        logger.error("Could not run command: %s" % str(e))
        return json_response(error="Could not run command: %s" % str(e), status="ERROR", status_code=500)


def get_systems():
    return ['localhost']
