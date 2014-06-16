from newt.views import JSONRestView
from common.response import json_response
from django.conf import settings
import urllib

job_adapter = __import__(settings.NEWT_CONFIG['ADAPTERS']['JOB'], globals(), locals(), ['adapter'], -1)

import logging
logger = logging.getLogger(__name__)


class JobRootView(JSONRestView):
    def get(self, request):
        return job_adapter.get_queues()

class JobQueueView(JSONRestView):
    def get(self, request, queue):
        return job_adapter.view_queue(request, queue)
    def post(self, request, queue):
        return job_adapter.submit_job(request, queue)

class JobDetailView(JSONRestView):
    def get(self, request, queue, job_id):
        return job_adapter.get_info(queue, job_id)

    def delete(self, request, queue, job_id):
        return job_adapter.delete_job(queue, job_id)