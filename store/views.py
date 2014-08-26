from newt.views import JSONRestView
from common.response import json_response
from django.conf import settings
import json
from importlib import import_module

store_adapter = import_module(settings.NEWT_CONFIG['ADAPTERS']['STORES']['adapter'])

import logging


logger = logging.getLogger("newt." + __name__)

# /api/store/
class StoreRootView(JSONRestView):
    def get(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return store_adapter.get_store(request)

    def post(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        initial_data = request.POST.getlist("data")
        return store_adapter.create_store(request, initial_data=initial_data)

# /api/store/<store_name>/
class StoreView(JSONRestView):
    def get(self, request, store_name):
        if request.GET.get("query", False):
            # Queries the store if the query parameter is set
            return store_adapter.query_store(request, store_name, request.GET.get("query"))
        else:
            # Returns all data about the store
            return store_adapter.get_store_contents(request, store_name)

    def post(self, request, store_name):

        if store_name in store_adapter.get_store(request):
            # Updates data if the store already exists
            initial_data = request.POST.get("data", None)
            return store_adapter.store_insert(request, store_name, initial_data=initial_data)
        else:
            # Creates and adds the data if the store doesn't exist
            initial_data = request.POST.getlist("data")
            return store_adapter.create_store(request, store_name, initial_data=initial_data)

    def delete(self, request, store_name):
        return store_adapter.delete_store(request, store_name)

# /api/store/<store_name>/perms/
class StorePermView(JSONRestView):
    def get(self, request, store_name):
        return store_adapter.get_store_perms(request, store_name)

    def post(self, request, store_name):
        perms = json.loads(request.POST.get("data", "[]"))
        return store_adapter.update_store_perms(request, store_name, perms=perms)

# /api/store/<store_name>/<obj_id>/
class StoreObjView(JSONRestView):
    def get(self, request, store_name, obj_id):
        return store_adapter.store_get_obj(request, store_name, obj_id)

    def put(self, request, store_name, obj_id):
        data = json.loads(request.body).get("data", None)
        if not data:
            return json_response(status="ERROR", status_code=400, error="No data received.")
        return store_adapter.store_update(request, store_name, obj_id, data=data)

# /api/store/<query>/
class ExtraStoreView(JSONRestView):
    def get(self, request, query):
        return acct_adapter.extras_router(request, query)