from newt.views import JSONRestView
from common.response import json_response
from django.conf import settings
import urllib

from importlib import import_module
job_adapter = import_module(settings.NEWT_CONFIG['ADAPTERS']['JOB']['adapter'])

import logging
logger = logging.getLogger("newt." + __name__)


# /api/jobs
class JobRootView(JSONRestView):
    def get(self, request):
        return job_adapter.get_queues()

# /api/jobs/<machine>/
class JobQueueView(JSONRestView):
    def get(self, request, machine):
        return job_adapter.view_queue(request, machine)
    def post(self, request, machine):
        return job_adapter.submit_job(request, machine)

# /api/jobs/<machine>/<job_id>/
class JobDetailView(JSONRestView):
    def get(self, request, machine, job_id):
        return job_adapter.get_info(machine, job_id)

    def delete(self, request, machine, job_id):
        return job_adapter.delete_job(machine, job_id)

# /api/jobs/<query>/
class ExtraJobView(JSONRestView):
    def get(self, request, query):
        return acct_adapter.extras_router(request, query)