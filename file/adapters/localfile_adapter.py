
from common.shell import run_command
import re

def get(machine_name, path):
    filehandle = open(path, 'r')
    return filehandle
    
    
def get_dir(machine_name, path):
    command = 'ls -la %s' % path
    (output, error, retcode) = run_command(command)

    # import pdb; pdb.set_trace()
    # Split the lines
    output = map(lambda i: i.strip(), output.split('\n'))


    # "awesome" regular expression that captures ls output of the form:
    # drwxrwxr-x   4  shreyas     newt        32768 Apr 15 10:59 home
    patt=re.compile(r'([\+\w@-]{10,})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\w{3}\s+\d+\s+[\d\:]+)\s+(.+)$')

    # filter out stuff that doesn't match pattern
    output = filter(lambda line: patt.match(line), output)
    # break up line into tuple: (perms, hl, user, group, size, date, filename)        
    output = map(lambda line: patt.match(line).groups(), output)

    # create a dict
    output = map(lambda groups: dict(zip(('perms', 'hardlinks', 'user', 'group', 'size', 'date', 'name'), groups)), output)
    
    return (output, error, retcode)
    
    
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
    
    
def put(request, machine, path):

    assert request.method == "PUT"

    # The file contents are in the raw_post_data 
    data = request.raw_post_data
        
    #Create tmp file
    with open(path, 'w') as fh
        fh.write(data)
    return {'location': request.path }
    
     