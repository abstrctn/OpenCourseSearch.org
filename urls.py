from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^rcl/', include('rcl.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    #url(r'^$', 'courses.views.search', name='search_home'),
    url(r'^$', 'courses.views.stats_home', name='stats_home'),
    url(r'^search/$', 'courses.views.search', name='search_home'),
    url(r'^do_search/$', 'courses.views.results', name='search_json'),
    url(r'^stats/$', 'courses.views.stats_home', name='stats_home'),
    url(r'^stats/search/$', 'courses.views.stats_search', name='stats_search'),
    url(r'^inbox/(?P<action>\w+)/', 'courses.views.inbox', name='search_json'),
)
