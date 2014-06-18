from newt.views import JSONRestView
from common.response import json_response
from django.conf import settings
import json
from importlib import import_module

store_adapter = import_module(settings.NEWT_CONFIG['ADAPTERS']['STORES']['adapter'])

import logging


logger = logging.getLogger(__name__)

class StoresRootView(JSONRestView):
    def get(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return store_adapter.get_stores()

    def post(self, request):
        logger.debug("Entering %s:%s" % (self.__class__.__name__, __name__))
        return store_adapter.create_store(request, "")


class StoresView(JSONRestView):
    def get(self, request, store_name):
        if request.GET.get("query", False):
            # Queries the store if the query parameter is set
            return store_adapter.query_store(store_name, request.GET.get("query"))
        else:
            # Returns all data about the store
            return store_adapter.get_store_contents(store_name)

    def post(self, request, store_name):
        if store_name in store_adapter.get_stores():
            # Updates data if the store already exists
            return store_adapter.store_insert(request, store_name)
        else:
            # Creates and adds the data if the store doesn't exist
            return store_adapter.create_store(request, store_name)

    def delete(self, request, store_name):
        return store_adapter.delete_store(store_name)

class StoresPermView(JSONRestView):
    def get(self, request, store_name):
        return store_adapter.get_store_perms(store_name)

    def post(self, request, store_name):
        return store_adapter.update_store_perms(request, store_name)


class StoresObjView(JSONRestView):
    def get(self, request, store_name, obj_id):
        return store_adapter.store_get_obj(store_name, obj_id)

    def put(self, request, store_name, obj_id):
        return store_adapter.store_update(request, store_name, obj_id)