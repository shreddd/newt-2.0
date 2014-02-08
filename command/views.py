# Create your views here.
# Create your views here.
from newt.views import JSONRestView
from common.response import json_response
from django.conf import settings
import urllib

command_adapter = __import__(settings.NEWT_CONFIG['ADAPTERS']['COMMAND'], globals(), locals(), ['adapter'], -1)

import logging


logger = logging.getLogger(__name__)

class CommandRootView(JSONRestView):
    def get(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return command_adapter.get_systems()


class CommandView(JSONRestView):
    def post(self, request, machine_name):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        command = urllib.unquote(request.POST['command'])
        
        try:
            response = command_adapter.post(machine_name, command)
        except Exception as e:
            logger.error("Could not run command: %s" % str(e))
            return json_response(error="Could not run command: %s" % str(e), status="ERROR", status_code=500)  
            
        return response