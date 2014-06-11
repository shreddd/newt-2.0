from django.conf.urls import patterns

from stores.views import *


urlpatterns = patterns('command.views',
    (r'^/?$', StoresRootView.as_view()),
    (r'^/(?P<store_name>[^/]+)/$', StoresView.as_view()),
    (r'^/(?P<store_name>[^/]+)/perms/$', StoresPermView.as_view()),
    (r'^/(?P<store_name>[^/]+)/(?P<obj_id>\d+)/$', StoresObjView.as_view()),
)
    
