from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^site-media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    
    url(r'^$', 'networks.views.session_home'),
    
    url(r'^stats/search/$', 'courses.views.stats_search', name='stats_search'),
    url(r'^inbox/(?P<action>\w+)/', 'courses.views.inbox', name='search_json'),
    
    url(r'^api/register/', 'api.views.register', name='api_register'),
    (r'^api/', include('api.proxy_urls')),
    (r'^(?P<session_slug>[-\w]+)/', include('networks.urls')),
)
