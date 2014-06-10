from newt.views import JSONRestView
from common.response import json_response
from django.shortcuts import render
from django.conf import settings

acct_adapter = __import__(settings.NEWT_CONFIG['ADAPTERS']['ACCOUNT'], globals(), locals(), ['adapter'], -1)

class UserInfoView(JSONRestView):
    def get(self, request, user_name=None, uid=None):
        return acct_adapter.get_user_info(user_name=user_name, uid=uid)

class GroupInfoView(JSONRestView):
    def get(self, request, group_name=None, gid=None):
        return acct_adapter.get_group_info(group_name=group_name, gid=gid)

class OtherInfoView(JSONRestView):
    def get(self, request, query):
        return json_response(status="Unimplemented", 
                             status_code=501, 
                             error="", 
                             content="query: %s" % query)