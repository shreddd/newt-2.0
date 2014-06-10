from django.contrib.auth.models import User, Group
from django.forms.models import model_to_dict
from common.response import json_response

def get_user_info(user_name, uid):
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
        if user_name:
            return json_response(status="ERROR", 
                                 status_code=404, 
                                 error="User not found: No user has the username %s" % user_name)
        else:
            return json_response(status="ERROR", 
                                 status_code=404, 
                                 error="User not found: No user has the id %s" % uid)

def get_group_info(group_name, gid):
    try:
        if gid:
            group = Group.objects.get(pk=gid)
        elif group_name:
            group = Group.objects.get(name=group_name)
        else:
            raise Exception()
        group_dict = model_to_dict(group)
        group_dict['users'] = [u.username for u in group.user_set.all()]
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