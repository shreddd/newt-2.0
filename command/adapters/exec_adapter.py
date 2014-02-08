from common.shell import run_command

def post(machine_name, command):
    (output, error, retcode) = run_command(command)
    response = {
        'stdout': output,
        'stderr': error,
        'retcode': retcode
    }
    return response
    