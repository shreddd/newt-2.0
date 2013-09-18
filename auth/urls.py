from django.conf.urls import patterns

from auth.views import AuthView


urlpatterns = patterns('auth.views',
    (r'^/?$', AuthView.as_view()),
)
    
