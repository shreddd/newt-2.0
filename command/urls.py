from django.conf.urls import patterns

from command.views import CommandView, CommandRootView


urlpatterns = patterns('command.views',
    (r'^/?$', CommandRootView.as_view()),
    (r'^/(?P<machine_name>[^/]+)$', CommandView.as_view()),
)
    
