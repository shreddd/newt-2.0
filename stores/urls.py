from django.conf.urls import patterns

from stores.views import StoresView, StoresRootView, StoresObjView


urlpatterns = patterns('command.views',
    (r'^/?$', StoresRootView.as_view()),
    (r'^/(?P<store_name>[^/]+)/$', StoresView.as_view()),
    (r'^/(?P<store_name>[^/]+)/(?P<obj_id>[^/]+)/$', StoresObjView.as_view()),
)
    
