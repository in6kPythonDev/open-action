try:
    from django.conf.urls import patterns, url
except ImportError as e:
    # Using Django < 1.4
    from django.conf.urls.defaults import patterns, url

import organization.views as org_views

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', org_views.OrgView.as_view(),
        name='org-detail'
    ),
    url(r'^(?P<pk>\d+)/follow/$', org_views.UserFollowOrgView.as_view(),
        name='org-user-follow'
    ),
    #KO: we must not enable this feature through web POSTs
    #KO: if we would like to implement such a thing we could wonder about
    #TODOFUTURE: a user create an action_request.ActionRequest asking the staff (null recipient)
    #TODOFUTURE: to be set as representative for an organization
    #KO: url(r'^(?P<pk>\d+)/represent/$', org_views.UserRepresentOrgView.as_view(),
    #KO:    name='org-user-represent'
    #KO:),
)
