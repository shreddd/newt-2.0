# Create your views here.
from newt.views import JSONRestView
from django.http import HttpResponseServerError
from django.conf import settings

# from status.adapters import XXXX as adapter
adapter = __import__(settings.NEWT_CONFIG['ADAPTERS']['STATUS'], globals(), locals(), ['adapter'], -1)


import logging
import json


logger = logging.getLogger(__name__)


class StatusView(JSONRestView):
    def get(self, request, machine_name=None):
        try:
            response = adapter.get(machine_name)
        except Exception as e:
            logger.error("Could not get status %s" % str(e))
            return HttpResponseServerError("Could not get status")  
            
        return response
