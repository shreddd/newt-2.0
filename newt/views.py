# Create your views here.
from django.views.generic.base import View
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.conf import settings

class JSONRestView(View):
    
    def dispatch(self, request, *args, **kwargs):
        # Wrap the dispatch method, so that we autoencode JSON
        response = super(JSONRestView, self).dispatch(request, *args, **kwargs)
        if not isinstance(response, HttpResponse):
            response = json.dumps(response, cls=DjangoJSONEncoder)
        return HttpResponse(response, content_type='application/json')


class RootView(JSONRestView):
    def get(self, request):
        
        response = {
            "status": "OK",
            "output": {
                "text": "Welcome to NEWT",
                "version": "0.5.0"
            },
            "error": ""
        }
        return response