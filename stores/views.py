from newt.views import JSONRestView
from common.response import json_response
from django.conf import settings
import json

store_adapter = __import__(settings.NEWT_CONFIG['ADAPTERS']['STORES'], globals(), locals(), ['adapter'], -1)

import logging


logger = logging.getLogger(__name__)

class StoresRootView(JSONRestView):
    def get(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return store_adapter.get_stores()

    def post(self, request):
        # Temporary: creates a store with a random name if no name is specified
        import uuid
        import random
        import string

        rand_key = random.choice(string.ascii_letters) + str(uuid.uuid4())[0:8]
        while(rand_key in store_adapter.get_stores()):
            rand_key = str(uuid.uuid4())[0:8]

        if request.POST.get("data", False):
            return store_adapter.create_store(rand_key, [request.POST.get("data")])
        else:
            return store_adapter.create_store(rand_key)


class StoresView(JSONRestView):
    def get(self, request, store_name):
        try:
            if request.GET.get("query", False):
                data = store_adapter.query_store(store_name, request.GET.get("query"))
            else:
                data = store_adapter.get_store_contents(store_name)
        except Exception as e:
            logger.error("Invalid store requested: %s", store_name)
            return json_response(status="ERROR", status_code=500, error=e.args[0])
        return data

    def post(self, request, store_name):
        if store_name in store_adapter.get_stores():
            if request.POST.get("data", False):
                data = request.POST.get("data")
                return store_adapter.store_insert(store_name, data)
            else:
                return json_response(status="ERROR", status_code=500, error="No data recieved.")
        else:
            if request.POST.get("data", False):
                return store_adapter.create_store(store_name, [request.POST.get("data")])
            else:
                return store_adapter.create_store(store_name)

    def put(self, request, store_name):
        data = json.loads(request.read())
        store_adapter.update(store_name, data)

    def delete(self, request, store_name):
        return store_adapter.delete_store(store_name)


class StoresObjView(JSONRestView):
    def get(self, request, store_name, obj_id):
        try:
            return store_adapter.store_get_obj(store_name, obj_id)
        except Exception as e:
            return json_response(status="ERROR", status_code="500", error=e.args[0])

    def put(self, request, store_name, obj_id):
        from django.http import QueryDict
        body = QueryDict(request.body)
        if body.get("data", False):
            data = body.get("data")
            return store_adapter.store_update(store_name, obj_id, data)
        else:
            return json_response(status="ERROR", status_code=500, error="No data recieved.")