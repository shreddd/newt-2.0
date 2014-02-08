# Create your views here.
from newt.views import JSONRestView
from django.conf import settings

auth_adapter = __import__(settings.NEWT_CONFIG['ADAPTERS']['AUTH'], globals(), locals(), ['adapter'], -1)


import logging

logger = logging.getLogger(__name__)



class AuthView(JSONRestView):


    def get(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        
        return auth_adapter.get(request)

    def post(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))

        return auth_adapter.post(request)        



    def delete(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        
        return auth_adapter.delete(request)


