from django.conf.urls import patterns

from status.views import StatusView, ExtraStatusView


urlpatterns = patterns('status.views',
    (r'^/?$', StatusView.as_view()),
    (r'^/(?P<machine_name>[^/]+)$', StatusView.as_view()),
    (r'^(?P<query>.+)/$', ExtraStatusView.as_view()),
)
    
