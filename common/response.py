from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json

def json_response(content="", status="OK", status_code=200, error=""):
    """
    Returns an HTTP response with standard JSON envelope
    """
    wrapper = {
        'status': status,
        'status_code': status_code,
        'output': content,
        'error': error
    }
    response = json.dumps(wrapper, cls=DjangoJSONEncoder)
    return HttpResponse(response, content_type='application/json', status=status_code)