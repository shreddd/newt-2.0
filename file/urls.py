from django.conf.urls import patterns

from file.views import FileView


urlpatterns = patterns('file.views',
    (r'^/(?P<machine_name>[^/]+)(?P<path>/.*)$', FileView.as_view()),
)
    
