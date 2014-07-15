from common.response import json_response
import logging
logger = logging.getLogger("newt." + __name__)
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
    username = request.POST['username'].encode("utf-8")
    password = request.POST['password'].encode("utf-8")

    logger.debug("Attempting to log in user: %s" % username)
    user = mpb.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        logger.info("Successfully logged in user: %s" % username)
    return get_status(request)


def logout(request):
    """Logs the user out and returns the status

    Keyword arguments:
    request -- Django HttpRequest
    """
    logger.info("Successfully logged out user: %s" % request.user.username)
    auth.logout(request)
    return get_status(request)


patterns = (
)

def extras_router(request, query):
    """Maps a query to a function if the pattern matches and returns result

    Keyword arguments:
    request -- Django HttpRequest
    query -- the query to be matched against
    """
    for pattern, func, req in patterns:
        match = pattern.match(query)
        if match and req:
            return func(request, **match.groupdict())
        elif match:
            return func(**match.groupdict())

    # Returns an Unimplemented response if no pattern matches
    return json_response(status="Unimplemented", 
                             status_code=501, 
                             error="", 
                             content="query: %s" % query)