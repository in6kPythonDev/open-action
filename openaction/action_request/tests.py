from django.core.urlresolvers import reverse
from django.conf import settings

from action.tests import OpenActionViewTestCase
from action_request.models import ActionRequest
from action import const
from action_request import exceptions as action_request_exceptions
from action_request.signals import action_moderation_request_submitted, action_moderation_request_processed
from oa_notification.handlers import notify_action_moderation_request, notify_action_moderation_processed
from notification.models import Notice, NoticeType
from oa_notification import models as oa_notification

import datetime

class ActionRequestModerationTest(OpenActionViewTestCase):

    def setUp(self):
        super(ActionRequestModerationTest, self).setUp()
        #manually connect signal to handler 
        action_moderation_request_submitted.connect(notify_action_moderation_request)
        action_moderation_request_processed.connect(notify_action_moderation_processed)
        #manually create notice types
        oa_notification.create_notice_types("","","")

        for notice_type in NoticeType.objects.all():
            print "added notice_type %s" % notice_type
        
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

    def _do_POST_process_action_moderation_request(self, action_request, ajax=False, **kwargs):

        response = self._POST(
            reverse('actionrequest-moderation-process', args=(action_request.pk,)),
            ajax,
            **kwargs
        )
        return response
#--------------------------------------------------------------------------------

    def test_create_action_moderation_request(self, user=None):

        follower = self.create_user(username='user2')

        self._login(follower)

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
            self.assertTrue(follower.is_following_action(self._action))

            #sending moderation request
            #follower = self.create_user(username='follower')
            request_text = "Ti chiedo di moderare la mia action"

            response = self._do_POST_create_action_moderation_request(action=self._action,
                ajax=True,
                follower=follower.pk,
                request_text=request_text
            )

            print "\n\n----------------response %s\n\n" % response

            self._check_for_redirect_response(response, is_ajax=True)
 
            try:
                action_req_objs = ActionRequest.objects.filter(action=self._action,
                    sender=login_user,
                    recipient=follower,
                    request_notes=request_text
                )
            except ActionRequest.DoesNotExist as e:
                action_req_objs = False

            self.assertTrue(action_req_objs)
            self.assertTrue(action_req_objs.count() == 1)


            #testing that the action owner cannot send more than three notices
            response = self._do_POST_create_action_moderation_request(action=self._action,
                ajax=True,
                follower=follower.pk,
                request_text=request_text
            )
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                action_req_objs = ActionRequest.objects.filter(action=self._action,
                    sender=login_user,
                    recipient=follower,
                    request_notes=request_text
                )
            except ActionRequest.DoesNotExist as e:
                action_req_objs = False

            self.assertTrue(action_req_objs)
            self.assertTrue(action_req_objs.count() == 2)

            response = self._do_POST_create_action_moderation_request(action=self._action,
                ajax=True,
                follower=follower.pk,
                request_text=request_text
            )
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                action_req_objs = ActionRequest.objects.filter(action=self._action,
                    sender=login_user,
                    recipient=follower,
                    request_notes=request_text
                )
            except ActionRequest.DoesNotExist as e:
                action_req_objs = False

            self.assertTrue(action_req_objs)
            self.assertTrue(action_req_objs.count() == 3)

            action_req_obj_first = action_req_objs[0]
            action_req_obj_second = action_req_objs[1]
            action_req_obj_third = action_req_objs[2]

            response = self._do_POST_create_action_moderation_request(action=self._action,
                ajax=True,
                follower=follower.pk,
                request_text=request_text
            )
            self._check_for_error_response(response, 
                e=action_request_exceptions.CannotRequestModerationToUser
            )

            #test that only the action owner can ask for moderation
            self._login(follower)
            response = self._do_POST_create_action_moderation_request(action=self._action,
                ajax=True,
                follower=follower.pk,
                request_text=request_text
            )
            self._check_for_error_response(response, 
                e=action_request_exceptions.RequestActionModerationNotOwnerException
            )

            #test the signal sending and handling
            notice_type = NoticeType.objects.get(label="mod_proposal")
            try:
                notice_obj = Notice.objects.filter(recipient=follower, 
                    notice_type=notice_type
                )
            except Notice.DoesNotExist as e:
                notice_obj = False

            self.assertTrue(notice_obj)
            self.assertTrue(notice_obj.count() <= settings.MAX_MODERATION_REQUESTS)

            #test the follower user response
            answer_text = "non mi va di moderare la tua action del cavolo"

            response = self._do_POST_process_action_moderation_request(action_request=action_req_obj_first,
                ajax=True,
                accept_request=0,
                answer_text=answer_text
            )

            self._check_for_redirect_response(response, is_ajax=True)

            action_request_not_accepted = ActionRequest.objects.get(pk=action_req_obj_first.pk)

            self.assertTrue(action_request_not_accepted.is_processed)
            self.assertTrue(not action_request_not_accepted.is_accepted)
            self.assertTrue(
                action_request_not_accepted.answer_notes == answer_text
            )
            
            notice_type = NoticeType.objects.get(label="answer_mod_proposal")
            try:
                notice_obj = Notice.objects.get(recipient=login_user, 
                    notice_type=notice_type
                )
            except Notice.DoesNotExist as e:
                notice_obj = False

            self.assertTrue(notice_obj)

            #test the follower user response
            answer_text = "che figata, accetto subito!"

            response = self._do_POST_process_action_moderation_request(action_request=action_req_obj_second,
                ajax=True,
                accept_request=1,
                answer_text=answer_text
            )

            self._check_for_redirect_response(response, is_ajax=True)

            action_request_accepted = ActionRequest.objects.get(pk=action_req_obj_second.pk)

            self.assertTrue(action_request_accepted.is_processed)
            self.assertTrue(action_request_accepted.is_accepted)
            self.assertTrue(
                action_request_accepted.answer_notes == answer_text
            )

            #test the follower user response
            answer_text = "mmh on mi ricordo se ho accettato, accetto ora per sicurezza"

            response = self._do_POST_process_action_moderation_request(action_request=action_req_obj_third,
                ajax=True,
                accept_request=1,
                answer_text=answer_text
            )

            self._check_for_redirect_response(response, is_ajax=True)

            act_req_accepted_sencond_time = ActionRequest.objects.get(pk=action_req_obj_third.pk)

            self.assertTrue(act_req_accepted_sencond_time.is_processed)
            self.assertTrue(not act_req_accepted_sencond_time.is_accepted)
            self.assertTrue(
                act_req_accepted_sencond_time.answer_notes == answer_text
            )
