from django.conf.urls.defaults import *
from users.forms import UserProfileForm
from users.views import UserDetailView, UserProfileListView, UserProfileDetailView, RegistrationOA
from django.contrib.auth.models import User

urlpatterns = patterns('',
    url(r'^(?P<username>\w+)/$',
        UserDetailView.as_view(
         model=User,
         context_object_name='registered_user',
         template_name='users/user_detail.html',
    ), name='users_user_detail'),
    url(r'^profile/(?P<username>\w+)/$',
        UserProfileDetailView.as_view(),
       name='profiles_profile_detail'),
    url(r'^$',
        UserProfileListView.as_view(),
       name='profiles_profile_list'),
    url(r'^register/$',
        RegistrationOA.as_view(),
       name='OA_registration'),
    #url(r'^profile/(?P<username>\w+)/details/$',
    #    UserProfileDetailView.as_view(),
    #   name='user-profile-details'),
)

#urlpatterns += patterns('profiles.views',
#    url(r'^profile/edit/$',
#       'edit_profile',
#       { 'form_class': UserProfileForm },
#       name='profiles_edit_profile'),
#    url(r'^profile/(?P<username>\w+)/$',
#        UserProfileDetailView.as_view(),
#       name='profiles_profile_detail'),
#    url(r'^$',
#        UserProfileListView.as_view(),
#       name='profiles_profile_list'),
#    url(r'^profile/(?P<username>\w+)/$',
#        UserProfileView.as_view(),
#       name='user-profile-details'),
#)
