from newt.views import JSONRestView
from common.response import json_response
from django.shortcuts import render
from django.conf import settings

acct_adapter = __import__(settings.NEWT_CONFIG['ADAPTERS']['ACCOUNT'], globals(), locals(), ['adapter'], -1)

class AcctInfoView(JSONRestView):
    def get(self, request, path):
        return acct_adapter.get_resource(path)

class UsageView(JSONRestView):
    def get(self, request, query):
        return acct_adapter.get_usage(query)

class ImgView(JSONRestView):
    def get(self, request, query):
        return acct_adapter.get_image(query)