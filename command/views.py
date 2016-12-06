from newt.views import JSONRestView
from common.response import json_response
from django.conf import settings
import urllib

from importlib import import_module
command_adapter = import_module(settings.NEWT_CONFIG['ADAPTERS']['COMMAND']['adapter'])

import logging
logger = logging.getLogger("newt." + __name__)


# /api/command/
class CommandRootView(JSONRestView):
    def get(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return command_adapter.get_systems(request)

# /api/command/<machine_name>/
class CommandView(JSONRestView):
    def post(self, request, machine_name):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        command = urllib.unquote(request.POST['command'])
        if not command:
            return json_response(status="ERROR", 
                                 status_code=400, 
                                 error="No command received.")
        return command_adapter.execute(request, machine_name, command)

# /api/command/<query>/
class ExtraCommandView(JSONRestView):
    def get(self, request, query):
        return command_adapter.extras_router(request, query)