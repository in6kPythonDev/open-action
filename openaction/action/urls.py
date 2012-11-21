try:
    from django.conf.urls import patterns, url
except ImportError as e:
    # Using Django < 1.4
    from django.conf.urls.defaults import patterns, url

import action.views as action_views
import action_request.views as action_request_views

urlpatterns = patterns('',
    # Single action view
    url(r'^(?P<pk>\d+)/$', action_views.ActionDetailView.as_view(), 
        name='action-detail'
    ),
    url(r'^create/$', action_views.ActionCreateView.as_view(), 
        name='action-create'
    ),
    url(r'^(?P<pk>\d+)/edit/$', action_views.ActionUpdateView.as_view(),
        name='action-update'
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
    #follow/unfollow action
    url(r'^(?P<pk>\d+)/follow/$', action_views.ActionFollowView.as_view(), 
        name='action-follow'
    ),
    url(r'^(?P<pk>\d+)/unfollow/$', action_views.ActionUnfollowView.as_view(), 
        name='action-unfollow'
    ),
    #request to a user to moderate action
    url(r'^(?P<pk>\d+)/moderator/add/$', action_request_views.ActionModerationRequestView.as_view(), 
        name='action-moderation-request'
    ),
    #private message between same Action referrers
    url(r'^(?P<pk>\d+)/message/send/$', action_request_views.ActionMessageRequestView.as_view(), 
        name='action-message-send'
    ),
    #remove moderator
    url(r'^(?P<pk>\d+)/moderator/remove/$', action_views.ActionModerationRemoveView.as_view(), 
        name='action-moderation-remove'
    ),
    #request to change action status to the staff
    url(r'^(?P<pk>\d+)/status/change/$', action_request_views.ActionSetStatusRequestView.as_view(), 
        name='action-status-change-request'
    ),

    #categories navigation
    url(r'^argument/(?P<pk>\d+)/$', action_views.CategoryActionListView.as_view(),
        name='category-action-list'
    ),

    #geonames navigation
    url(r'^location/(?P<pk>\d+)/$', action_views.GeonameListView.as_view(),
        name='geoname-action-list'
    ),

)

