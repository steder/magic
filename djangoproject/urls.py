import os

from django.conf.urls.defaults import include, patterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import settings


urlpatterns = patterns('',
    # Example:
    # (r'^djangoproject/', include('djangoproject.foo.urls')),
    (r'^$', 'djangoproject.views.index'),
    (r'^magic/', include('djangoproject.magic.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

)

if settings.DEBUG:
    # handle static files
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$',
         'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT,
          "show_indexes":True})
    )
