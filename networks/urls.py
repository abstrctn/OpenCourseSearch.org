from django.conf.urls.defaults import *

urlpatterns = patterns('networks.views',
    url(r'index^$', 'index', name='network_index'),
    url(r'^$', 'session_home', name='session_home'),
    #url(r'^(?P<slugs>[-\w\/\.]+)/$', 'course', name='course_detail'),
    url(r'^(?P<slugs>.+)/$', 'course', name='course_detail'),
)