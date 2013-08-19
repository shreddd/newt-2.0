# Create your views here.
from django.views.generic.base import View
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json

class JSONRestView(View):
    
    def dispatch(self, request, *args, **kwargs):
        # Wrap the dispatch method, so that we autoencode JSON
        response = super(JSONRestView, self).dispatch(request, *args, **kwargs)
        if not isinstance(response, HttpResponse):
            response = json.dumps(response, cls=DjangoJSONEncoder)
        return HttpResponse(response, content_type='application/json')


