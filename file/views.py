from newt.views import JSONRestView
from common.response import json_response
from django.http import HttpResponse, HttpResponseServerError, StreamingHttpResponse
from django.conf import settings

from importlib import import_module
file_adapter = import_module(settings.NEWT_CONFIG['ADAPTERS']['FILE']['adapter'])


import logging


logger = logging.getLogger(__name__)


class FileRootView(JSONRestView):
    def get(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return file_adapter.get_systems(request)

class FileView(JSONRestView):
    def get(self, request, machine_name, path):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        if request.GET.get("download", False):
            return file_adapter.download_path(request, machine_name, path)
        else:
            return file_adapter.get_dir(request, machine_name, path)
        
    def put(self, request, machine_name, path):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return file_adapter.put_file(request, machine_name, path)

class ExtraFileView(JSONRestView):
    def get(self, request, query):
        return acct_adapter.extras_router(request, query)