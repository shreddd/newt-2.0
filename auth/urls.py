from django.conf.urls import patterns

from auth.views import AuthView, ExtraAuthView


urlpatterns = patterns('auth.views',
    (r'^/?$', AuthView.as_view()),
    (r'^(?P<query>.+)/$', ExtraAuthView.as_view()),
)
    
