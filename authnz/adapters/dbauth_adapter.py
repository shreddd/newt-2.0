from django.contrib import auth
import logging
import re
logger = logging.getLogger("newt." + __name__)

def is_logged_in(request):
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


def get_status(request):
    return is_logged_in(request)


def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(username=username, password=password)

    logger.debug("Attemping to log in user: %s" % username)

    if user is not None:
        auth.login(request, user)
        logger.info("Successfully logged in user: %s" % username)

    return is_logged_in(request)

def logout(request):
    logger.info("Successfully logged out user: %s" % request.user.username)

    auth.logout(request)

    return is_logged_in(request)

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