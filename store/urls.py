from django.conf.urls import patterns

from store.views import *


urlpatterns = patterns('command.views',
    (r'^/?$', StoreRootView.as_view()),
    (r'^/(?P<store_name>[^/]+)/$', StoreView.as_view()),
    (r'^/(?P<store_name>[^/]+)/perms/$', StorePermView.as_view()),
    (r'^/(?P<store_name>[^/]+)/(?P<obj_id>\d+)/$', StoreObjView.as_view()),
    (r'^(?P<query>.+)/$', ExtraStoreView.as_view()),
)
    
