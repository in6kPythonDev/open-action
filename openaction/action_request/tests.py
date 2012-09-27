from django.core.urlresolvers import reverse
from django.conf import settings

from action.tests import OpenActionViewTestCase
from action_request.models import ActionRequest
from action import const
from action_request import exceptions as action_request_exceptions

import datetime

class ActionRequestModerationTest(OpenActionViewTestCase):

    def setUp(self):
        super(ActionRequestModerationTest, self).setUp()
        self._action = self._create_action(title="Action N#1")

 
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

    def _do_POST_create_action_moderation_request(self, action, ajax=False, **kwargs):

        response = self._POST(
            reverse('action-moderation-request', args=(action.pk,)),
            ajax,
            **kwargs
        )
        return response

    def _do_GET_create_action_moderation_request(self, action, ajax=False):

        response = self._GET(
            reverse('action-moderation-request', args=(action.pk,)),
            ajax
        )
        return response

#--------------------------------------------------------------------------------

    def test_create_action_moderation_request(self, user=None):

        user2 = self.create_user(username='user2')

        self._login(user2)

        #action = self._create_action()

        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        #response = self._do_POST_follow_action(
        #    action=self._action,
        #    ajax=True
        #)
        response = self._POST(
            reverse('action-follow', args=(self._action.pk,)),
            is_ajax=True
        )

        logged_in = self._login(user)

        if logged_in:
            #success
            self._check_for_success_response(response)
            #check that user is following action
            login_user = [self._author, user][bool(user)]
            #self.assertTrue(login_user.is_following_action(self._action))
            self.assertTrue(user2.is_following_action(self._action))

            #sending moderation request
            #user2 = self.create_user(username='user2')
            request_text = "Ti chiedo di moderare la mia action"

            response = self._do_POST_create_action_moderation_request(action=self._action,
                ajax=True,
                follower=user2.pk,
                request_text=request_text
            )

            print "\n\n----------------response %s\n\n" % response

            self._check_for_redirect_response(response, is_ajax=True)
 
            try:
                action_req_objs = ActionRequest.objects.filter(action=self._action,
                    sender=login_user,
                    recipient=user2,
                    request_notes=request_text
                )
            except ActionRequest.DoesNotExist as e:
                action_req_objs = False

            self.assertTrue(action_req_objs)
            self.assertTrue(action_req_objs.count() == 1)

            #testing that the action owner cannot send more than three notices
            response = self._do_POST_create_action_moderation_request(action=self._action,
                ajax=True,
                follower=user2.pk,
                request_text=request_text
            )
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                action_req_objs = ActionRequest.objects.filter(action=self._action,
                    sender=login_user,
                    recipient=user2,
                    request_notes=request_text
                )
            except ActionRequest.DoesNotExist as e:
                action_req_objs = False

            self.assertTrue(action_req_objs)
            self.assertTrue(action_req_objs.count() == 2)

            response = self._do_POST_create_action_moderation_request(action=self._action,
                ajax=True,
                follower=user2.pk,
                request_text=request_text
            )
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                action_req_objs = ActionRequest.objects.filter(action=self._action,
                    sender=login_user,
                    recipient=user2,
                    request_notes=request_text
                )
            except ActionRequest.DoesNotExist as e:
                action_req_objs = False

            self.assertTrue(action_req_objs)
            self.assertTrue(action_req_objs.count() == 3)

            response = self._do_POST_create_action_moderation_request(action=self._action,
                ajax=True,
                follower=user2.pk,
                request_text=request_text
            )
            self._check_for_error_response(response, 
                e=action_request_exceptions.CannotRequestModerationToUser
            )

            #test that only the action owner can ask for moderation
            self._login(user2)
            response = self._do_POST_create_action_moderation_request(action=self._action,
                ajax=True,
                follower=user2.pk,
                request_text=request_text
            )
            self._check_for_error_response(response, 
                e=action_request_exceptions.RequestActionModerationNotOwnerException
            )

            #test the signal sending and handling
            
