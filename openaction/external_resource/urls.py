
from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

from external_resource.views import proxy, cityreps_proxy

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<backend_name>\w+)/(?P<url>.*)', proxy, name='external_proxy'),
#    url(r'^cityreps/(?P<url>.*)', cityreps_proxy, name='cityreps_external_proxy'),
)
