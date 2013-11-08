# Create your views here.
from django.views.generic.base import View
from django.http import HttpResponse
from django.http.response import HttpResponseBase
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from newt.common.response import json_response

import json
import os

class JSONRestView(View):
    """
    This is the core class that everything else should subclass in NEWT
    This provides all the hooks to make the JSON friendly
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override the dispatch method of the class view 
        """
        # Wrap the dispatch method, so that we autoencode JSON
        response = super(JSONRestView, self).dispatch(request, *args, **kwargs)
        # If this is not an HTTPResponseBase object (Base class for responses) 
        if not isinstance(response, HttpResponseBase):
            response = json_response(response)

        return response

    # By default return a 501 - each API call needs to implement what it needs
    def get(self, request, *args, **kwargs):
        return json_response(error="Not Implemented", status="ERROR", status_code=501)
    
    def post(self, request, *args, **kwargs):
        return json_response(error="Not Implemented", status="ERROR", status_code=501)
    
    def put(self, request, *args, **kwargs):
        return json_response(error="Not Implemented", status="ERROR", status_code=501)
    
    def delete(self, request, *args, **kwargs):
        return json_response(error="Not Implemented", status="ERROR", status_code=501)
    



class RootView(JSONRestView):
    def get(self, request):
        """
        The top level NEWT URL
        """
        response = {
                "text": "Welcome to NEWT",
                "version": settings.NEWT_VERSION
        }

        return response

    def post(self, request):
        return json_response(error="Not Implemented", status="ERROR", status_code=501)


        
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
        # Don't go through the JSONRestView for this, because it has to comply with the swagger format  
        return HttpResponse(response, content_type='application/json')
        
        