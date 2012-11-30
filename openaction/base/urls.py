from django.conf.urls.defaults import *
from views import HomepageView

urlpatterns = patterns('',
    url(r'^$',
        HomepageView.as_view(
            template_name='homepage.html',
        ), name='homepage'),
)