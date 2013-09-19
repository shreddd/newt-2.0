# Create your views here.
from newt.views import JSONRestView

from django.contrib.auth import authenticate, login, logout

import logging

logger = logging.getLogger(__name__)



class AuthView(JSONRestView):

    def is_logged_in(self, request):
        if (request.user is not None) and (request.user.is_authenticated()):
            output=dict(auth=True,
                        username=request.user.username,
                        session_lifetime=request.session.get_expiry_age())
        else:
            output=dict(auth=False,
                        username=None,
                        session_lifetime=0)
        return output


    def get(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        
        return self.is_logged_in(request)

    def post(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

        return self.is_logged_in(request)


    def delete(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        
        logout(request)
        return self.is_logged_in(request)

