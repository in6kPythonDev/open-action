try:
    from django.conf.urls import patterns, url
except ImportError as e:
    # Using Django < 1.4
    from django.conf.urls.defaults import patterns, url

import action_request.views as ar_views

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/answer/$', ar_views.ActionRequestModerationProcessView.as_view(),
        name='actionrequest-moderation-process'
    ),
)
