from common.response import json_response

from django.contrib import auth
import logging
import re


# See https://docs.djangoproject.com/en/1.10/howto/auth-remote-user/
#
# Configuration
#
# First, you must add the django.contrib.auth.middleware.RemoteUserMiddleware
# to the MIDDLEWARE setting after the
# django.contrib.auth.middleware.AuthenticationMiddleware:
#
# MIDDLEWARE = [
#     '...',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.auth.middleware.RemoteUserMiddleware',
#     '...',
# ]
#
# Next, you must replace the ModelBackend with RemoteUserBackend in the
# AUTHENTICATION_BACKENDS setting:
#
# AUTHENTICATION_BACKENDS = [
#     'django.contrib.auth.backends.RemoteUserBackend',
# ]
#
# With this setup, RemoteUserMiddleware will detect the username in
# request.META['REMOTE_USER'] and will authenticate and auto-login that user
# using the RemoteUserBackend.


logger = logging.getLogger("newt." + __name__)


def is_logged_in(request):
    if (request.user is not None) and (request.user.is_authenticated()):
        output = dict(auth=True,
                      username=request.user.username,
                      session_lifetime=request.session.get_expiry_age(),
                      newt_sessionid=request.session.session_key)
    else:
        output = dict(auth=False,
                      username=None,
                      session_lifetime=0,
                      newt_sessionid=None)
    return output


def get_status(request):
    return is_logged_in(request)


def login(request):
    # Use RemoteUserBackend.authenicate instead?
    user = request.user

    if (request.user is not None) and (not request.user.is_authenticated()):
        logger.debug("Attemping to log in user: %s" % user.username)
        auth.login(request, user)
        logger.info("Successfully logged in user: %s" % user.username)

    return is_logged_in(request)


def logout(request):
    logger.info("Successfully logged out user: %s" % request.user.username)

    auth.logout(request)

    return is_logged_in(request)

patterns = (
    (re.compile(r'/login'), login, True),
    (re.compile(r'/logout'), logout, True),
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
