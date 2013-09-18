# Create your views here.
from newt.views import JSONRestView
from django.http import HttpResponseServerError
from status.adapters import passthrough_adapter as adapter

import logging
import json


logger = logging.getLogger(__name__)


class StatusView(JSONRestView):
    def get(self, request, machine_name=None):
        
        try:
            response = adapter.get(machine_name)
        except Exception as e:
            logger.error("Could not connect to Status Service %s" % str(e))
            return HttpResponseServerError("Could not connect to Status Service")  
            
        return response
        
        