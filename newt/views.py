# Create your views here.
from django.views.generic.base import View
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
import json
import os

class JSONRestView(View):
    """
    This is the core class that everything else should subclass in NEWT
    This provides all the hooks to make the JSON friendly
    """
    def dispatch(self, request, *args, **kwargs):
        # Wrap the dispatch method, so that we autoencode JSON
        response = super(JSONRestView, self).dispatch(request, *args, **kwargs)
        if not isinstance(response, HttpResponse):
            response = json.dumps(response, cls=DjangoJSONEncoder)
            
        # Possibly fill out the missing fields in the response
        response = HttpResponse(response, content_type='application/json')

        return response

class RootView(JSONRestView):
    def get(self, request):
        """
        The top level NEWT URL
        """
        response = {
            "status": "OK",
            "output": {
                "text": "Welcome to NEWT",
                "version": settings.NEWT_VERSION
            },
            "error": ""
        }
        return response
        
class DocView(View):
    """
    Implements a Swagger API doc
    http://swagger.wordnik.com/

    Don't go through the JSONRestView for this, because it has to comply with the swagger format
    """
    
    def get(self, request, path=None):
        base_path = os.path.join(settings.PROJECT_DIR, "newt", "api-docs")
        filename = "index.json"
        if path==None:
            doc = os.path.join(base_path, filename)
        else:
            doc = os.path.join(base_path, path, filename)
            
        with open(doc) as doc_file:
            response = doc_file.read()
            
        return HttpResponse(response, content_type='application/json')
        
        