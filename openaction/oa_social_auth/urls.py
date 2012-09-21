# Taken AS IS from https://github.com/omab/django-social-auth/tree/master/example

from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

# Example Django social-auth views
from oa_social_auth.views import home, done, logout, error

# New Django social-auth login forms
from oa_social_auth.views import login_form
from oa_social_auth.facebook import facebook_view
#from app.vkontakte import vkontakte_view
#from app.odnoklassniki import ok_app, ok_app_info

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^done/$', done, name='done'),
    url(r'^login-error/$', error, name='error'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^login-form/$', login_form, name='login-form'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^fb/', facebook_view, name='fb_app'),
#    url(r'^vk/', vkontakte_view, name='vk_app'),
#    url(r'^ok/$', ok_app , name='ok_app'),
#    url(r'^ok/info/$', ok_app_info , name='ok_app_info'),
    url(r'', include('social_auth.urls')),
)
