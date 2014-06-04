
from common.shell import run_command
import re
import magic
import logging


logger = logging.getLogger(__name__)


def get(machine_name, path):
    filehandle = open(path, 'r')
    return filehandle
    
    
def put(request, machine, path):

    assert request.method == "PUT"

    upload_handlers = request.upload_handlers
    content_type   = str(request.META.get('CONTENT_TYPE', ""))
    content_length = int(request.META.get('CONTENT_LENGTH', 0))

    if content_type == "":
        return HttpResponse(status=400)
    if content_length == 0:
        # both returned 0
        return HttpResponse(status=400)

    content_type = content_type.split(";")[0].strip()
    try:
        charset = content_type.split(";")[1].strip()
    except IndexError:
        charset = ""
    counters = [0]*len(upload_handlers)

    for handler in upload_handlers:
        result = handler.handle_raw_input("",request.META,content_length,"","")

    for handler in upload_handlers:
        try:
            handler.new_file("file", "test.pdf", 
                             content_type, content_length, charset)
        except Exception:
            break

    for i, handler in enumerate(upload_handlers):
        while True:
            chunk = request.read(handler.chunk_size)
            if chunk:

                handler.receive_data_chunk(chunk, counters[i])
                counters[i] += len(chunk)
            else:
                # no chunk
                break

    for i, handler in enumerate(upload_handlers):
        file_obj = handler.file_complete(counters[i])
        if not file_obj:
            raise Exception("Upload Error")
        else:
            with open(path, "w") as fh:
                file_obj.seek(0)
                fh.write(file_obj.read())
            return { 'location': path }
    
    
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
    output = map(lambda line: patt.match(line).groups() + ("",) , output)

    # create a dict
    output = map(lambda groups: dict(zip(('perms', 'hardlinks', 'user', 'group', 'size', 'date', 'name', 'symlink'), groups)), output)
    
    for line in output:
        if line['perms'].startswith('l'):
            name, symlink = line['name'].split(' -> ')
            line['name'] = name
            line['symlink'] = symlink
    
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
    
def get_systems():
    return ['localhost']
     