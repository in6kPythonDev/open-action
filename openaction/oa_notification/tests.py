"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.urlresolvers import reverse

from askbot.models import Post, User
from askbot.models.repute import Vote

from action import const, exceptions
from oa_notification import models as oa_notification
from notification.models import Notice, NoticeType
from action.tests import ActionViewTest
#signals handling
from action.signals import post_action_status_update
from oa_notification.handlers import notify_post_status_update

from lib import views_support

import os, urllib2

#---------------------------------------------------------------------------------

class OaNotificationTest(ActionViewTest):

    def setUp(self):
        super(ActionViewTest, self).setUp()
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
            old_status=const.ACTION_STATUS_READY
        )

        notice_type = NoticeType.objects.get(label="joined_action_get_level_step")
        try:
            notice_obj = Notice.objects.get(recipient=self._author, 
                notice_type=notice_type
            )
        except Notice.DoesNotExist as e:
            notice_obj = False

        self.assertTrue(notice_obj)
