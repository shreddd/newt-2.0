from common.shell import run_command
import re
import magic
import logging
from django.http import StreamingHttpResponse
from common.response import json_response
import tempfile
from common.decorators import login_required

logger = logging.getLogger("newt." + __name__)


def get_mime_type(machine_name=None, path=None, file_handle=None):
    if file_handle:
        try:
            content_type = magic.from_buffer(file_handle.read(1024), mime=True)
        except Exception as e:
            logger.warning("Could not get mime type %s" % str(e))
            content_type = 'application/octet-stream'
        file_handle.seek(0)
    elif path:
        try:
            content_type = magic.from_file(path)
        except Exception as e:
            logger.warning("Could not get mime type %s" % str(e))
            content_type = 'application/octet-stream'
    else:
        content_type = 'application/octet-stream'
    return content_type   


def download_path(request, machine_name, path):
    try:
        file_handle = open(path, 'r')
        content_type = get_mime_type(machine_name, path, file_handle)
        logger.debug("File download requested: %s" % path)
        return StreamingHttpResponse(file_handle, content_type=content_type)
    except Exception as e:
        logger.error("Could not get file %s" % str(e))
        return json_response(status="ERROR",
                             status_code=500,
                             error=str(e))
    
    
def put_file(request, machine, path):
    data = request.read()
    # Write data to temporary location
    # TODO: Get temporary path from settings.py 
    tmp_file = tempfile.NamedTemporaryFile(prefix="newt_")
    tmp_file.write(data)
    tmp_file.file.flush()

    src = tmp_file.name
    dest = path

    (output, error, retcode) = run_command("cp %s %s" % (src, dest))
    if retcode != 0:
        return json_response(content=output, status="ERROR", status_code=500, error=error)
    tmp_file.close()
    return {'location': path}
    
   
def get_dir(request, machine_name, path):
    try:
        command = 'ls -la %s' % path
        (output, error, retcode) = run_command(command)

        if retcode != 0:
            return json_response(content=output, status="ERROR", status_code=500, error=error)

        # import pdb; pdb.set_trace()
        # Split the lines
        output = map(lambda i: i.strip(), output.split('\n'))

        # "awesome" regular expression that captures ls output of the form:
        # drwxrwxr-x   4  shreyas     newt        32768 Apr 15 10:59 home
        patt=re.compile(r'(?P<perms>[\+\w@-]{10,})\s+(?P<hardlinks>\d+)\s+(?P<user>\S+)\s+(?P<group>\S+)\s+(?P<size>\d+)\s+(?P<date>\w{3}\s+\d+\s+[\d\:]+)\s+(?P<name>.+)$')

        # filter out stuff that doesn't match pattern
        output = filter(lambda line: patt.match(line), output)

        # Convert output into dict from group names
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
    return ['localhost']

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