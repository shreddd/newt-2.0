# Create your views here.
from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseServerError
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
        # If this is a regular python object 
        if not isinstance(response, HttpResponse):
            response = self.wrap_response(response)
            response = HttpResponse(response, content_type='application/json')
        # TODO: Think about how to handle django errors vs. newt erros
        # How do you bubble up errors from NEWT?
        else:
            if response.status_code >= 200 and response.status_code <= 299:
                response.content = self.wrap_response(response.content, status="OK", status_code=response.status_code, error = '')
            else:
                response.content = self.wrap_response('', status="ERROR", status_code=response.status_code, error = response.content)

        return response

    def wrap_response(self, content, status="OK", status_code=200, error=""):
        wrapper = {
            'status': status,
            'status_code': status_code,
            'output': content,
            'error': error
        }
        response = json.dumps(wrapper, cls=DjangoJSONEncoder)
        return response


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
        return HttpResponse("Not Implemented", status=501)


        
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
        
        