from newt.views import JSONRestView
from common.response import json_response
from django.http import HttpResponse, HttpResponseServerError, StreamingHttpResponse
from django.conf import settings

file_adapter = __import__(settings.NEWT_CONFIG['ADAPTERS']['FILE'], globals(), locals(), ['adapter'], -1)


import logging


logger = logging.getLogger(__name__)


class FileRootView(JSONRestView):
    def get(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return file_adapter.get_systems()

class FileView(JSONRestView):
    def get(self, request, machine_name, path):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        if request.GET.get("download", False):
            return file_adapter.download_path(machine_name, path)
        else:
            return file_adapter.get_dir(machine_name, path)
        
    def put(self, request, machine_name, path):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return file_adapter.put_file(request, machine_name, path)