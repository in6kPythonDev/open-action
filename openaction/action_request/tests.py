from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from action.tests import OpenActionViewTestCase
from action_request.models import ActionRequest
from action import const
from action_request import consts as ar_consts
from askbot_extensions import consts as ae_consts
from action_request import exceptions as action_request_exceptions
from action_request.signals import action_moderation_request_submitted, action_moderation_request_processed
from oa_notification.handlers import notify_action_moderation_request, notify_action_moderation_processed
from notification.models import Notice, NoticeType
from oa_notification import models as oa_notification
from askbot.models.user import Activity

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

        self.follower = self.create_user(username='user2')
        self._login(self.follower)
        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)
        
        self._POST(
            reverse('action-follow', args=(self._action.pk,)),
            is_ajax=True
        )
        ##success
        #self._check_for_success_response(response)
        ##self.assertTrue(login_user.is_following_action(self._action))
        #self.assertTrue(self.follower.is_following_action(self._action))
 
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

    def _do_POST_remove_action_moderator(self, action, ajax=False, **kwargs):

        response = self._POST(
            reverse('action-moderation-remove', args=(action.pk,)),
            ajax,
            **kwargs
        )
        return response

    def _do_POST_change_action_status_request(self, action, ajax=False, **kwargs):

        response = self._POST(
            reverse('action-status-change-request', args=(action.pk,)),
            ajax,
            **kwargs
        )
        return response

    def _get_moderation_request_objs(self, 
        action, 
        sender, 
        recipient, 
        request_notes
    ):
        try:
            action_req_objs = ActionRequest.objects.filter(
                action=action,
                sender=sender,
                recipient=recipient,
                request_notes=request_notes
            )
        except ActionRequest.DoesNotExist as e:
            action_req_objs = False

        return action_req_objs

    def _get_notice_objs(self,
        notice_label,
        recipient
    ):
        notice_type = NoticeType.objects.get(label=notice_label)
        try:
            notice_obj = Notice.objects.filter(recipient=recipient, 
                notice_type=notice_type
            )
        except Notice.DoesNotExist as e:
            notice_obj = False

        return notice_obj

#--------------------------------------------------------------------------------

    def test_only_action_owner_can_ask_moderation(self):

        request_text = "Sono un moderatore, vorresti darmi una mano a moderare questa action?"
    
        self._login(self.follower)
        response = self._do_POST_create_action_moderation_request(
            action=self._action,
            ajax=True,
            follower=self.follower.pk,
            request_text=request_text
        )
        self._check_for_error_response(response, 
            e=action_request_exceptions.RequestActionModerationNotOwnerException
        )

    def test_create_action_moderation_request(self, user=None):

        logged_in = self._login(user)

        if logged_in:

            login_user = [self._author, user][bool(user)]

            #sending moderation request
            request_text = "Ti chiedo di moderare la mia action"

            response = self._do_POST_create_action_moderation_request(
                action=self._action,
                ajax=True,
                follower=self.follower.pk,
                request_text=request_text
            )

            #print "\n\n----------------response %s\n\n" % response

            self._check_for_redirect_response(response, is_ajax=True)
 
            action_req_objs = self._get_moderation_request_objs( 
                    action=self._action,
                    sender=login_user,
                    recipient=self.follower,
                    request_notes=request_text
            )

            self.assertTrue(action_req_objs)
            self.assertTrue(action_req_objs.count() == 1)

    def test_action_owner_cannot_send_more_than_three_notices(self, user=None):

        logged_in = self._login(user)
        login_user = [self._author, user][bool(user)]
        request_text = "Ti chiedo di moderare la mia action"
        n_tries = [1,2,3]

        if logged_in:

            for n_try in n_tries:
                response = self._do_POST_create_action_moderation_request(
                    action=self._action,
                    ajax=True,
                    follower=self.follower.pk,
                    request_text=request_text
                )
                self._check_for_redirect_response(response, is_ajax=True)

                #checking request #n_try
                action_req_objs = self._get_moderation_request_objs( 
                        action=self._action,
                        sender=login_user,
                        recipient=self.follower,
                        request_notes=request_text
                )
                self.assertTrue(action_req_objs)
                self.assertTrue(action_req_objs.count() == n_try)

            #response = self._do_POST_create_action_moderation_request(
            #    action=self._action,
            #    ajax=True,
            #    follower=self.follower.pk,
            #    request_text=request_text
            #)
            #self._check_for_redirect_response(response, is_ajax=True)

            ##checking request #2
            #action_req_objs = self._get_moderation_request_objs( 
            #        action=self._action,
            #        sender=login_user,
            #        recipient=self.follower,
            #        request_notes=request_text
            #)
            #self.assertTrue(action_req_objs)
            #self.assertTrue(action_req_objs.count() == 2)

            #response = self._do_POST_create_action_moderation_request(
            #    action=self._action,
            #    ajax=True,
            #    follower=self.follower.pk,
            #    request_text=request_text
            #)
            #self._check_for_redirect_response(response, is_ajax=True)

            ##checking request #3
            #action_req_objs = self._get_moderation_request_objs( 
            #        action=self._action,
            #        sender=login_user,
            #        recipient=self.follower,
            #        request_notes=request_text
            #)
            #self.assertTrue(action_req_objs)
            #self.assertTrue(action_req_objs.count() == 3)

            #action_req_obj_first = action_req_objs[0]
            #action_req_obj_second = action_req_objs[1]
            #action_req_obj_third = action_req_objs[2]

            response = self._do_POST_create_action_moderation_request(
                action=self._action,
                ajax=True,
                follower=self.follower.pk,
                request_text=request_text
            )
            self._check_for_error_response(response, 
                e=action_request_exceptions.CannotRequestModerationToUser
            )

            notice_obj = self._get_notice_objs(notice_label="mod_proposal", 
                recipient=self.follower
            )
            self.assertTrue(notice_obj)
            self.assertTrue(notice_obj.count() <= settings.MAX_MODERATION_REQUESTS)


    def test_follower_user_responses(self, user=None):

        logged_in = self._login(user)
        login_user = [self._author, user][bool(user)]
        request_text = "Ti chiedo di moderare la mia action"
        request_type = ar_consts.REQUEST_TYPE_MODERATION
        action_requests = [0,1,2]

        if logged_in:

            for a_r in action_requests:
                n = int(a_r)
                action_requests[n] = ActionRequest(
                    action=self._action,
                    sender=login_user,
                    recipient=self.follower,
                    request_notes=request_text,
                    request_type=request_type 
                )
                action_requests[n].save()
        else:
            raise Exception

        for a_r in action_requests:
            print("\naction_requests_created.pk=%s\n" % a_r.pk)
        for a_r in ActionRequest.objects.all():
            print("\naction_requests.pk=%s\n" % a_r.pk)

        logged_in = self._login(self.follower)

        if logged_in:
            answer_text = "non mi va di moderare la tua action del cavolo"

            response = self._do_POST_process_action_moderation_request(action_request=action_requests[0],
                ajax=True,
                accept_request=0,
                answer_text=answer_text
            )


            #print("RESPONSE-----------------------: %s" % response)

            self._check_for_redirect_response(response, is_ajax=True)

            action_request_not_accepted = ActionRequest.objects.get(pk=action_requests[0].pk)
            print("\nis_accepted=%s\n" % action_request_not_accepted.is_accepted)
            self.assertTrue(action_request_not_accepted.is_processed)
            self.assertTrue(not action_request_not_accepted.is_accepted)
            self.assertTrue(
                action_request_not_accepted.answer_notes == answer_text
            )

            notice_obj = self._get_notice_objs(
                notice_label="answer_mod_proposal",
                recipient=login_user
            )

            self.assertTrue(notice_obj)

            #test the follower user response
            answer_text = "che figata, accetto subito!"

            response = self._do_POST_process_action_moderation_request(action_request=action_requests[1],
                ajax=True,
                accept_request=1,
                answer_text=answer_text
            )

            self._check_for_redirect_response(response, is_ajax=True)

            action_request_accepted = ActionRequest.objects.get(pk=action_requests[1].pk)

            self.assertTrue(action_request_accepted.is_processed)
            self.assertTrue(action_request_accepted.is_accepted)
            self.assertTrue(
                action_request_accepted.answer_notes == answer_text
            )

            #test the follower user response
            answer_text = "mmh non mi ricordo se ho accettato, accetto ora per sicurezza"

            response = self._do_POST_process_action_moderation_request(action_request=action_requests[2],
                ajax=True,
                accept_request=1,
                answer_text=answer_text
            )

            self._check_for_redirect_response(response, is_ajax=True)

            act_req_accepted_sencond_time = ActionRequest.objects.get(pk=action_requests[2].pk)

            self.assertTrue(act_req_accepted_sencond_time.is_processed)
            self.assertTrue(not act_req_accepted_sencond_time.is_accepted)
            self.assertTrue(
                act_req_accepted_sencond_time.answer_notes == answer_text
            )

    def test_update_action_active_status_register(self, user=None):
        """ Test whether a new Activity is registered when the Action owner 
        asks to set the Action status to VICTORY (the staff will have to 
        accept or decline the request) """

        logged_in = self._login(user)
        login_user = [self._author, user][bool(user)]

        request_text = "Vorrei impostare l'azione come vittoriosa"
        request_type = ar_consts.REQUEST_TYPE_SET_VICTORY
        status_to_set = const.ACTION_STATUS_VICTORY

        if logged_in:

            #ActionRequest
            response = self._do_POST_change_action_status_request(
                action=self._action,
                ajax=True,
                request_text=request_text,
                status_to_set=status_to_set
            )

            print("\n\n----------------response: %s\n" % response)

            self._check_for_redirect_response(response, is_ajax=True)

            ctype = ContentType.objects.get_for_model(self._action.__class__)
            obj_pk = self._action.pk
            try:
                activity_obj = Activity.objects.get(
                    user=[self._author, user][bool(user)],
                    content_type=ctype,
                    object_id=obj_pk,
                    activity_type=ae_consts.OA_TYPE_ACTIVITY_SET_VICTORY,
                    question=self._action.question
                )
            except Activity.DoesNotExist as e:
                activity_obj = False

            self.assertTrue(activity_obj)

            #ActionRequest #2 (same)
            response = self._do_POST_change_action_status_request(
                action=self._action,
                ajax=True,
                request_text=request_text,
                status_to_set=status_to_set
            )

            print("\n\n----------------response: %s\n" % response)

            self._check_for_error_response(response, 
                e=action_request_exceptions.ActionStatusUpdateRequestAlreadySent
            )

    def test_update_action_closed_status_register(self, user=None):
        """ Test whether a new Activity is registered when the Action owner 
        asks to set the Action status to VICTORY (the staff will have to 
        accept or decline the request) """

        logged_in = self._login(user)
        login_user = [self._author, user][bool(user)]

        request_text = "Vorrei chiudere l'azione"
        request_type = ar_consts.REQUEST_TYPE_SET_CLOSURE
        status_to_set = const.ACTION_STATUS_CLOSED

        if logged_in:

            #ActionRequest
            response = self._do_POST_change_action_status_request(
                action=self._action,
                ajax=True,
                request_text=request_text,
                status_to_set=status_to_set
            )

            print("\n\n----------------response: %s\n" % response)

            self._check_for_redirect_response(response, is_ajax=True)

            ctype = ContentType.objects.get_for_model(self._action.__class__)
            obj_pk = self._action.pk
            try:
                activity_obj = Activity.objects.get(
                    user=[self._author, user][bool(user)],
                    content_type=ctype,
                    object_id=obj_pk,
                    activity_type=ae_consts.OA_TYPE_ACTIVITY_SET_CLOSURE,
                    question=self._action.question
                )
            except Activity.DoesNotExist as e:
                activity_obj = False

            self.assertTrue(activity_obj)

            #ActionRequest #2 (same)
            response = self._do_POST_change_action_status_request(
                action=self._action,
                ajax=True,
                request_text=request_text,
                status_to_set=status_to_set
            )

            print("\n\n----------------response: %s\n" % response)

            self._check_for_error_response(response, 
                e=action_request_exceptions.ActionStatusUpdateRequestAlreadySent
            )

    def test_user_not_referrer_cannot_update_action_status(self):
        """ Test that a user cannot set the Action status  if he is not
        an Action referrer """

        self._login(self.follower)

        request_text = "Vorrei chiudere l'azione"
        request_type = ar_consts.REQUEST_TYPE_SET_CLOSURE
        status_to_set = const.ACTION_STATUS_CLOSED

        #ActionRequest
        response = self._do_POST_change_action_status_request(
            action=self._action,
            ajax=True,
            request_text=request_text,
            status_to_set=status_to_set
        )

        print("\n\n----------------response: %s\n" % response)

        self._check_for_error_response(response, 
            e=action_request_exceptions.UserCannotAskActionUpdate
        )
