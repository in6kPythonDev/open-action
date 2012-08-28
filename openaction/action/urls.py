try:
    from django.conf.urls import patterns, url
except ImportError as e:
    # Using Django < 1.4
    from django.conf.urls.defaults import patterns, url

from action.views import ActionDetailView

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', ActionDetailView.as_view(), 
        name='question-detail'
    ),
)

