# Create your views here.
import logging
from newt.views import JSONRestView
from django.conf import settings
from importlib import import_module

status_adapter = import_module(settings.NEWT_CONFIG['ADAPTERS']['STATUS']['adapter'])

logger = logging.getLogger("newt." + __name__)


class StatusView(JSONRestView):
    def get(self, request, machine_name=None):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return status_adapter.get_status(machine_name)


class ExtraStatusView(JSONRestView):
    def get(self, request, query):
        return status_adapter.extras_router(request, query)
