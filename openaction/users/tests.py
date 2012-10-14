from django.core.urlresolvers import reverse
from django.conf import settings

from action.tests import OpenActionViewTestCase
from action import const
from action_request import exceptions as ae_exceptions
from users.models import UserProfile
from organization.models import UserOrgMap
from lib import views_support

import datetime

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

    def _do_GET_show_user_profile_details(self, username):

        response = self._GET(
            reverse('user-profile-details', args=(username,)),
            False
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

        #follow ond represent organization
        org_name = "Organization 1"
        _org = self._create_organization(name=org_name)

        mapping, created = UserOrgMap.objects.get_or_create(user=login_user,
            org=_org,
            is_follower=True,
            is_representative=True
        )
        #join action
        timestamp = datetime.datetime.now()
        title = "title"
        text = "text"
        tagnames = "tagnames"

        question = login_user.post_question(
            title = title,
            body_text = text,
            tags=tagnames,
            wiki = False,
            is_anonymous = False,
            timestamp = timestamp
        )

        _action = question.action
 
        _action.compute_threshold()
        _action.update_status(const.ACTION_STATUS_READY)

        _action.vote_add(login_user)

        response = self._do_GET_show_user_profile_details(username)

        print "\nresponse_%s\n\n" % response
        #TODO: Matteo: I shouldn't test it like this, i should only test that 
        # the response returns an HttpResponseObject with hyyp_status_code 200
        #WAS: self._check_for_success_response(response)
        self.assertEqual(response.status_code, views_support.HTTP_SUCCESS)
