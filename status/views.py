# Create your views here.
from newt.views import JSONRestView
from common.response import json_response
from django.http import HttpResponseServerError
from django.conf import settings

from importlib import import_module
adapter = import_module(settings.NEWT_CONFIG['ADAPTERS']['STATUS']['adapter'])

import logging


logger = logging.getLogger(__name__)


class StatusView(JSONRestView):
    def get(self, request, machine_name=None):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return adapter.get_status(machine_name)

class ExtraStatusView(JSONRestView):
    def get(self, request, query):
        return acct_adapter.extras_router(request, query)