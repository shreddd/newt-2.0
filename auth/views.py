# Create your views here.
from newt.views import JSONRestView
from django.http import HttpResponseServerError
from django.conf import settings

from django.contrib.auth import authenticate, login, logout


# from status.adapters import XXXX as adapter

import logging
import json


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
        return self.is_logged_in(request)

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

        return self.is_logged_in(request)


    def delete(self, request):
        logout(request)
        return self.is_logged_in(request)

