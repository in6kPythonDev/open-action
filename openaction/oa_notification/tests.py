"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.urlresolvers import reverse
from django.test.client import Client

from askbot.models import Post, User
from askbot.models.repute import Vote

from action import const, exceptions
from oa_notification import models as oa_notification
from notification.models import Notice, NoticeType
from action.tests import ActionViewTest, OpenActionViewTestCase
#signals handling
from action.signals import post_action_status_update
from oa_notification.handlers import notify_post_status_update

from lib import views_support

import os, urllib2

#---------------------------------------------------------------------------------

class OaNotificationTest(ActionViewTest):

    def setUp(self):
        super(OaNotificationTest, self).setUp()
        #manually connect signal to handler 
        post_action_status_update.connect(notify_post_status_update)
        #manually create notice types
        oa_notification.create_notice_types("","","")

        for notice_type in NoticeType.objects.all():
            print "added notice_type %s" % notice_type

#-----------------TESTS----------------------------------------------------------

    def test_notify_action_get_level_step(self):
        """ """
        # add voter to action voters
        self.test_add_vote_to_ready_action()
        # change status
        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        #sending action status update signal
        post_action_status_update.send(sender=self._action, 
            old_status=const.ACTION_STATUS_READY,
            user=None
        )

        notice_type = NoticeType.objects.get(label="joined_action_get_level_step")
        try:
            notice_obj = Notice.objects.get(recipient=self._author, 
                notice_type=notice_type
            )
        except Notice.DoesNotExist as e:
            notice_obj = False

        self.assertTrue(notice_obj)

#TODO: integrate with the tests above.
#TODO: restructure test to prevent the action app tests to be executed here
#TODO: Test
class NotificationTest(OpenActionViewTestCase):

    def setUp(self):
        
        types = ["1","2","3","4","6"]
        
        for _type in types:
            self._create_notice_type(_type)
        
        # Create test user
        username = 'user1'
        self._author = self.create_user(username=username)

        self._c = Client()

    def _create_notice_type(self, _type):
        
        label = "Notifica tipo %s" % _type 
        display = "display tipo %s" % _type
        description = "description tipo %s" % _type
        default = 2

        noticetype, created = NoticeType.objects.get_or_create(label=label, 
            display=display,
            description=description,
            default=default
        )

        try:
            print "%s NoticeType object with pk %s" % (["Not created","Created"][created], noticetype.pk)
        except Exception as e:
            pass
 
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

    def _do_POST_notice_settings(self, ajax=False):

        response = self._POST(
            reverse('notification_notice_settings', args=()),
            ajax
        )
        return response

    def _do_GET_notice_settings(self, ajax=False):

        response = self._GET(
            reverse('notification_notice_settings', args=()),
            ajax
        )
        return response

#--------------------------------------------------------------------------------

    def test_notice_settings(self):

        self._login()

        response = self._do_POST_notice_settings(ajax=True)

        print "POST response status code %s" % response.status_code
        print "POST response content %s" % response.content

        response = self._do_GET_notice_settings(ajax=True)

        print "GET response status code %s" % response.status_code
        print "GET response content %s" % response.content

    def test_notify_action_xxxx_to_referres__and_followers(self):

        #TODO: make some action here and do something on it

        #check that all action referrers and followers has been notified
        #NOTE: a test for Action referrers has still to be done
        user2 = self.create_user(username='user2')
        self.test_follow_action(user2)

        try:
            user_follow_action = user2.followed_threads.get(
                pk=self._action.thread.pk
            )
        except Post.DoesNotExist as e:
            user_follow_action = False

        self.assertTrue(user_follow_action)

        #try:
        #    notice = Notice.objects.get(
        #        recipient=user2
        #    )
        #except Notice.DoesNotExist as e:
        #    notice = False

        #self.assertTrue(notice)
