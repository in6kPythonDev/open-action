try:
    from django.conf.urls import patterns, url
except ImportError as e:
    # Using Django < 1.4
    from django.conf.urls.defaults import patterns, url

from action.views import ActionDetailView, ActionVoteView, CommentVoteView,EditablePoliticianView,EditableParameterView
#DELETE just for testing
from action.views import TestView

urlpatterns = patterns('',
    #DELETE just for testing
    url(r'^$',TestView,name='test'),
    url(r'^(?P<pk>\d+)/$', ActionDetailView.as_view(), 
        name='action-detail'
    ),
    url(r'^question/(?P<pk>\d+)/vote/$', ActionVoteView.as_view(), 
        name='action-vote'
    ),
    url(r'^comment/(?P<pk>\d+)/vote/$', CommentVoteView.as_view(), 
        name='comment-vote'
    ),
    url(r'^(?P<pk>\d+)/edit/politicians/$', EditablePoliticianView.as_view(), 
        name='edit-politician'
    ),
    url(r'^(?P<pk>\d+)/edit/(?P<attr>\w+)/$', EditableParameterView.as_view(), 
        name='edit-parameter'
    ),
)

