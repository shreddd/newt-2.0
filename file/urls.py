from django.conf.urls import patterns

from file.views import FileView, FileRootView


urlpatterns = patterns('file.views',
    (r'^/?$', FileRootView.as_view()),
    (r'^/(?P<machine_name>[^/]+)(?P<path>/.*)$', FileView.as_view()),
)
    
