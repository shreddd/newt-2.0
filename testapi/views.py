# Create your views here.
from newt.views import JSONRestView
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json

class TestAPIView(JSONRestView):
    def get(self, request):
        return {"output": "hello world!"}
