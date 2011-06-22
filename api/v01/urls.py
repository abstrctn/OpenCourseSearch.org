from django.conf.urls.defaults import *

urlpatterns = patterns('api.v01.views',
  url(r'^course$', 'course', name='api_course'),
  url(r'^network$', 'network', name='api_course'),
  url(r'^session$', 'session', name='api_course'),
)