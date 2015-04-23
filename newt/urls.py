from django.conf.urls import patterns, include, url
from newt.views import RootView
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'newt.views.home', name='home'),
    # url(r'^newt/', include('newt.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    (r'^api/?$', RootView.as_view()),
    (r'^api/status', include('status.urls')),
    (r'^api/file', include('file.urls')),
    (r'^api/auth', include('authnz.urls')),
    (r'^api/command', include('command.urls')),
    (r'^api/store', include('store.urls')),
    (r'^api/account', include('account.urls')),
    (r'^api/job', include('job.urls')),

)
