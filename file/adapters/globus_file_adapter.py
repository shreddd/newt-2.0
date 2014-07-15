"""File Adapter Template File

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
from django.http import StreamingHttpResponse
from common.response import json_response
import logging
logger = logging.getLogger("newt." + __name__)
from common.shell import run_command
from common import gridutil
import tempfile
import mimetypes

def download_path(request, machine_name, path):
    """Returns a StreamingHttpResponse with the file

    Keyword arguments:
    machine_name -- name of the machine
    path -- path to file
    """
    src = gridutil.get_grid_path(machine_name, path)
    env = gridutil.get_cred_env(request.user)
    dest = "/tmp/newt_"+request.user.username+"/"
    logger.debug("File download requested: %s (%s)" % (path, src))
    (output, error, retcode) = run_command(gridutil.GLOBUS_CONF['LOCATION'] + "bin/globus-url-copy %s %s" % (src, dest), env=env)
    if retcode != 0:
        logger.warning("Unable to download file: %s" % src)
        return json_response(content=output, status="ERROR", status_code=500, error=error)
    filename = path.rsplit("/")[-1]
    f = open(dest+"filename", "r")
    mimetype = mimetypes.guess_type(f.name)
    if mimetype is None:
        mimetype = "application/octet-stream"
    return StreamingHttpResponse(f, content_type=mimetype)

def put_file(request, machine, path):
    """Writes the uploaded file to path and returns the path

    Keyword arguments:
    request -- HttpRequest containing the data
    machine_name -- name of the machine
    path -- path to file
    """
    # Get data from request body
    data = request.read()
    # Write data to temporary location
    # TODO: Get temporary path from settings.py 
    tmp_file = tempfile.NamedTemporaryFile(prefix="newt_")
    tmp_file.write(data)
    tmp_file.file.flush()

    src = "file:///%s" % tmp_file.name
    env = gridutil.get_cred_env(request.user)
    dest = gridutil.get_grid_path(machine, path)

    logger.debug("Putting file to location: %s" % dest)

    (output, error, retcode) = run_command(gridutil.GLOBUS_CONF['LOCATION'] + "bin/globus-url-copy %s %s" % (src, dest), env=env)
    if retcode != 0:
        return json_response(content=output, status="ERROR", status_code=500, error=error)
    tmp_file.close()
    return {'location': path}


def get_dir(request, machine_name, path):
    """Returns a directory listing of path (as an array)

    Keyword arguments:
    machine_name -- name of the machine
    path -- path to file
    """
    try:
        env = gridutil.get_cred_env(request.user)
        path = gridutil.get_grid_path(machine_name, path)
        output, error, retcode = run_command(gridutil.GLOBUS_CONF['LOCATION'] + "bin/uberftp -ls %s" % path, 
                                              env=env)
        if retcode != 0:
            return json_response(content=output, status="ERROR", status_code=500, error=error)

        # Split the lines
        output = map(lambda i: i.strip(), output.splitlines())

        # regular expression that captures ls output of the form:
        # drwxrwxr-x   4  shreyas     newt        32768 Apr 15 10:59 home
        patt=re.compile(r'(?P<perms>[\+\w@-]{10,})\s+(?P<hardlinks>\d+)\s+(?P<user>\S+)\s+(?P<group>\S+)\s+(?P<size>\d+)\s+(?P<date>\w{3}\s+\d+\s+[\d\:]+)\s+(?P<name>.+)$')

        # filter out stuff that doesn't match pattern
        output = filter(lambda line: patt.match(line), output)
        # break up line into tuple: (perms, hl, user, group, size, date, filename)        
        output = map(lambda x: patt.match(x).groupdict(), output)

        for line in output:
            if line['perms'].startswith('l'):
                name, symlink = line['name'].split(' -> ')
                line['name'] = name
                line['symlink'] = symlink
            else:
                line['symlink'] = ""
        return output

    except Exception as e:
        logger.error("Could not get directory %s" % str(e))
        return json_response(status="ERROR", status_code=500, error="Could not get directory: %s" % str(e))


def get_systems(request):
    """Returns a list of all the systems available
    """
    return gridutil.GRID_RESOURCE_TABLE.keys()

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