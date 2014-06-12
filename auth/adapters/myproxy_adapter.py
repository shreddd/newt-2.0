from common.response import json_response
import logging
logger = logging.getLogger(__name__)
from auth.adapters.myproxy_backend import MyProxyBackend
from django.contrib import auth


def get_status(request):
    """Returns the current user status

    Keyword arguments:
    request -- Django HttpRequest
    """
    if (request.user is not None) and (request.user.is_authenticated()):
        output=dict(auth=True,
                    username=request.user.username,
                    session_lifetime=request.session.get_expiry_age(),
                    newt_sessionid=request.session.session_key)
    else:
        output=dict(auth=False,
                    username=None,
                    session_lifetime=0,
                    newt_sessionid=None)
    return output


def login(request):
    """Logs the user in and returns the status

    Keyword arguments:
    request -- Django HttpRequest
    """
    mpb = MyProxyBackend()
    username = request.POST['username']
    password = request.POST['password']
    user = mpb.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
    return get_status(request)


def logout(request):
    """Logs the user out and returns the status

    Keyword arguments:
    request -- Django HttpRequest
    """
    auth.logout(request)
    return get_status(request)