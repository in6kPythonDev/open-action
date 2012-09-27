
from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

from external_resource.views import proxy

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<backend_name>\w+)/(?P<url>.*)', proxy, name='external_proxy'),
)
