try:
    from django.conf.urls import patterns, url
except ImportError as e:
    # Using Django < 1.4
    from django.conf.urls.defaults import patterns, url

import action_request.views as action_request_views

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/answer/$', action_request_views.ActionRequestModerationProcessView.as_view(),
        name='actionrequest-moderation-process'
    ),
)
