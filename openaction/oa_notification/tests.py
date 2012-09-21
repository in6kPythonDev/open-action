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
from action.tests import ActionViewTest
#signals handling
from action.signals import post_action_status_update
from oa_notification.handlers import notify_action_get_level_step

from lib import views_support

import os, urllib2

#---------------------------------------------------------------------------------

class OaNotificationTest(ActionViewTest):

    def setUp(self):
        super(ActionViewTest, self).setUp()
        #manually connect signal to handler 
        post_action_status_update.connect(notify_action_get_level_step)
        #manually create notice types
        oa_notification.create_notice_types("","","")

        import notification
        for notice_type in notification.models.NoticeType.objects.all():
            print "added notice_type %s" % notice_type

#-----------------TESTS----------------------------------------------------------

    def test_notify_action_get_level_step(self):
        """ """
        # add voter to action voters
        self.test_add_vote_to_ready_action()
        # change status
        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        try:
            notice_obj = oa_notification.UserNotice.objects.get(user=self._author)
        except oa_notification.UserNotice.DoesNotExist as e:
            notice_obj = False

        self.assertTrue(notice_obj)
