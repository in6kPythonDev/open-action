from django.core.urlresolvers import reverse
from django.conf import settings

from action.tests import OpenActionViewTestCase
from action_request import exceptions as ae_exceptions
from users.models import UserProfile

class UsersTests(OpenActionViewTestCase):

    def setUp(self):
        super(UsersTests, self).setUp()
       
    def _POST(self, url, is_ajax, **kwargs):
        
        if is_ajax:
            response = self._c.post(url,
                kwargs,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
        else:
            response = self._c.post(url,
                kwargs
            )
        return response

    def _GET(self, url, is_ajax, **kwargs):
        
        if is_ajax:
            response = self._c.get(url,
                kwargs,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
        else:
            response = self._c.get(url,
                kwargs
            )
        return response

    #def _do_POST_show_user_profile_details(self, username, ajax=False, **kwargs):
    #    response = self._POST(
    #        reverse('user-profile-details', args=(username,)),
    #        ajax,
    #        **kwargs
    #    )
    #    return response

    def _do_GET_show_user_profile_details(self, username, ajax=False):

        response = self._GET(
            reverse('user-profile-details', args=(username,)),
            ajax
        )
        return response
    
    def _create_user_profile(self, 
        user,
        city,
        description
    ):

        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            city=city,
            description=description
        )

        try:
            #user_profile_obj = UserProfile.objects.get(
            #    pk=user_profile.pk
            #)
            user_profile_obj = UserProfile.objects.get(
                user__username='user1'
            )
        except Exception as e:
            user_profile_obj = False

        self.assertTrue(user_profile_obj)

        return user_profile

#--------------------------------------------------------------------------------

    def test_show_user_profile_details(self, user=None):

        logged_in = self._login(user)
        login_user = [self._author, user][bool(user)]

        username = login_user.username
        city = "Fabriano"
        description = "Che bella la mia homepage!"

        self._create_user_profile(
            user=login_user,
            city=city,
            description=description
        )

        response = self._do_GET_show_user_profile_details(username,
            ajax=True
        )

        print "\nresponse_%s\n\n" % response 
        self._check_for_success_response(response)
