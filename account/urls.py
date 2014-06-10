from django.conf.urls import patterns

from account.views import *


urlpatterns = patterns('account.views',
    (r'^/image/(?P<query>.+)$', ImgView.as_view()),
    (r'^/usage/(?P<query>.+)$', UsageView.as_view()),
    (r'^(?P<path>.+)$', AcctInfoView.as_view()),
)
