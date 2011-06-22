from django.conf.urls.defaults import *

urlpatterns = patterns('',
  url(r'^course$', 'api.proxy_views.proxy_course'),
  url(r'^network$', 'api.proxy_views.proxy_network'),
  url(r'^session$', 'api.proxy_views.proxy_session'),
)