from newt.views import JSONRestView
from newt.views import AuthJSONRestView
from common.response import json_response
from django.shortcuts import render
from django.conf import settings

import logging
logger = logging.getLogger("newt." + __name__)

from importlib import import_module
acct_adapter = import_module(settings.NEWT_CONFIG['ADAPTERS']['ACCOUNT']['adapter'])

# /api/account/user/<user_name>/
# /api/account/user/id/<uid>/
class UserInfoView(AuthJSONRestView):
    def get(self, request, user_name=None, uid=None):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return acct_adapter.get_user_info(user_name=user_name, uid=uid)

# /api/account/group/<group_name>/
# /api/account/group/<gid>/
class GroupInfoView(AuthJSONRestView):
    def get(self, request, group_name=None, gid=None):
        return acct_adapter.get_group_info(group_name=group_name, gid=gid)

# /api/account/<query>/
class ExtraAcctView(JSONRestView):
    def get(self, request, query):
        return acct_adapter.extras_router(request, query)