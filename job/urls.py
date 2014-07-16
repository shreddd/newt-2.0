from django.conf.urls import patterns

from job.views import *


urlpatterns = patterns('command.views',
    (r'^/?$', JobRootView.as_view()),
    (r'^/(?P<machine>[^/]+)/$', JobQueueView.as_view()),
    (r'^/(?P<machine>[^/]+)/(?P<job_id>[^/]+)/$', JobDetailView.as_view()),
    (r'^(?P<query>.+)/$', ExtraJobView.as_view()),
)
    
