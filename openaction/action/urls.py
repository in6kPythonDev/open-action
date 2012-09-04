try:
    from django.conf.urls import patterns, url
except ImportError as e:
    # Using Django < 1.4
    from django.conf.urls.defaults import patterns, url

import action.views as action_views

urlpatterns = patterns('',
    # Single action view
    url(r'^(?P<pk>\d+)/$', action_views.ActionDetailView.as_view(), 
        name='action-detail'
    ),
    url(r'^create/$', action_views.ActionCreateView.as_view(), 
        name='action-create'
    ),
    url(r'^(?P<pk>\d+)/vote/add/$', action_views.ActionVoteView.as_view(), 
        name='action-vote-add'
    ),
    url(r'^(?P<pk>\d+)/edit/politicians/$', action_views.EditablePoliticianView.as_view(), 
        name='edit-politician'
    ),
    url(r'^(?P<pk>\d+)/edit/(?P<attr>\w+)/$', action_views.EditableParameterView.as_view(), 
        name='edit-parameter'
    ),

    # Action related view (list of actions, comments for action, ...)
    url(r'^comment/(?P<pk>\d+)/vote/add/$', action_views.CommentVoteView.as_view(), 
        name='comment-vote-add'
    ),
    url(r'^(?P<pk>\d+)/comment/add/$', action_views.ActionCommentView.as_view(), 
        name='action-comment-add'
    ),
    
    url(r'^blogpost/(?P<pk>\d+)/comment/add/$', action_views.BlogpostCommentView.as_view(), 
        name='blogpost-comment-add'
    ),
    url(r'^(?P<pk>\d+)/blogpost/add/$', action_views.ActionBlogpostView.as_view(), 
        name='action-blogpost-add'
    ),
    url(r'^comment/(?P<pk>\d+)/vote/add/$', action_views.CommentVoteView.as_view(), 
        name='comment-vote'
    ),
)

