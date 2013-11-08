# Create your views here.
from newt.views import JSONRestView
from common.response import json_response
from django.http import HttpResponseServerError
from django.conf import settings

adapter = __import__(settings.NEWT_CONFIG['ADAPTERS']['STATUS'], globals(), locals(), ['adapter'], -1)

import logging


logger = logging.getLogger(__name__)


class StatusView(JSONRestView):
    def get(self, request, machine_name=None):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        try:
            response = adapter.get(machine_name)
        except Exception as e:
            logger.error("Could not get status: %s" % str(e))
            return json_response(error="Could not get status: %s" % str(e), status="ERROR", status_code=500)  
            
        return response