from django.conf.urls import patterns

from job.views import *


urlpatterns = patterns('command.views',
    (r'^/?$', JobRootView.as_view()),
    (r'^/(?P<queue>[^/]+)/$', JobQueueView.as_view()),
    (r'^/(?P<queue>[^/]+)/(?P<job_id>[^/]+)/$', JobDetailView.as_view()),
)
    
