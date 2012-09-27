try:
    from django.conf.urls import patterns, url
except ImportError as e:
    # Using Django < 1.4
    from django.conf.urls.defaults import patterns, url

import organization.views as organization_views

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', organization_views.OrgView.as_view(),
        name='org-detail'
    ),
    url(r'^(?P<pk>\d+)/follow/$', organization_views.UserFollowOrgView.as_view(),
        name='org-user-follow'
    ),
    url(r'^(?P<pk>\d+)/represent/$', organization_views.UserRepresentOrgView.as_view(),
        name='org-user-represent'
    ),
)
