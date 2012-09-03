try:
    from django.conf.urls import patterns, url
except ImportError as e:
    # Using Django < 1.4
    from django.conf.urls.defaults import patterns, url

from action.views import ActionDetailView, ActionVoteView, CommentVoteView,EditablePoliticianView,EditableParameterView, ActionCommentView, BlogpostCommentView, ActionAnswerView

urlpatterns = patterns('',
    # Single action view
    url(r'^(?P<pk>\d+)/$', ActionDetailView.as_view(), 
        name='action-detail'
    ),
    url(r'^(?P<pk>\d+)/vote/add/$', ActionVoteView.as_view(), 
        name='action-vote-add'
    ),
    url(r'^(?P<pk>\d+)/edit/politicians/$', EditablePoliticianView.as_view(), 
        name='edit-politician'
    ),
    url(r'^(?P<pk>\d+)/edit/(?P<attr>\w+)/$', EditableParameterView.as_view(), 
        name='edit-parameter'
    ),

    # Action related view (list of actions, comments for action, ...)
    url(r'^comment/(?P<pk>\d+)/vote/add/$', CommentVoteView.as_view(), 
        name='comment-vote-add'
    ),
    url(r'^(?P<pk>\d+)/comment/add/$', ActionCommentView.as_view(), 
        name='action-comment-add'
    ),
    
    url(r'^blogpost/(?P<pk>\d+)/comment/add/$', BlogpostCommentView.as_view(), 
        name='blogpost-comment-add'
    ),
    url(r'^(?P<pk>\d+)/blogpost/add/$', ActionAnswerView.as_view(), 
        name='action-blogpost-add'
    ),
)

