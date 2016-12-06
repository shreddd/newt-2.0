# Create your views here.
from newt.views import JSONRestView
from django.conf import settings

from importlib import import_module
auth_adapter = import_module(settings.NEWT_CONFIG['ADAPTERS']['AUTH']['adapter'])

import logging
logger = logging.getLogger("newt." + __name__)


# /api/auth/
class AuthView(JSONRestView):

    def get(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return auth_adapter.get_status(request)

    def post(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return auth_adapter.login(request)        

    def delete(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return auth_adapter.logout(request)

# /api/auth/<query>/
class ExtraAuthView(JSONRestView):
    def get(self, request, query):
        return auth_adapter.extras_router(request, query)