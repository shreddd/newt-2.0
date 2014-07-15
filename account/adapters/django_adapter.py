from django.contrib.auth.models import User, Group
from django.forms.models import model_to_dict
from common.response import json_response
import re
import logging
logger = logging.getLogger("newt."+__name__)

def get_user_info(user_name, uid):
    """Returns information about the user

    Keyword arguments:
    user_name -- username
    uid -- user id
    """
    try:
        if uid:
            user = User.objects.get(pk=uid)
        elif user_name:
            user = User.objects.get(username=user_name)
        else:
            raise Exception()
        user_dict = model_to_dict(user)
        del user_dict["password"]
        return user_dict
    except Exception:
        logger.debug("No user found matching query: %s" % (user_name if user_name else uid))
        if user_name:
            return json_response(status="ERROR", 
                                 status_code=404, 
                                 error="User not found: No user has the username %s" % user_name)
        else:
            return json_response(status="ERROR", 
                                 status_code=404, 
                                 error="User not found: No user has the id %s" % uid)

def get_group_info(group_name, gid):
    """Returns information about the group

    Keyword arguments:
    group_name -- group name
    gid -- group id
    """
    try:
        if gid:
            group = Group.objects.get(pk=gid)
        elif group_name:
            group = Group.objects.get(name=group_name)
        else:
            raise Exception()
        group_dict = model_to_dict(group)
        group_dict['users'] = [{"id": u.id, "username": u.username} for u in group.user_set.all()]
        return group_dict
    except Exception:
        if group_name:
            return json_response(status="ERROR", 
                                 status_code=404, 
                                 error="Group not found: No group matches the name %s" % group_name)
        else:
            return json_response(status="ERROR", 
                                 status_code=404, 
                                 error="Group not found: No group matches the id %s" % gid)

"""A tuple list in the form of:
    (
        (compiled_regex_exp, associated_function, request_required),
        ...
    )

    Note: The compiled_regex_exp must have named groups corresponding to
          the arguments of the associated_function
    Note: if request_required is True, the associated_function must have
          request as the first argument

    Example:
        patterns = (
            (re.compile(r'/usage/(?P<path>.+)$'), get_usage, False),
            (re.compile(r'/image/(?P<query>.+)$'), get_image, False),
            (re.compile(r'/(?P<path>.+)$'), get_resource, False),
        )
"""
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