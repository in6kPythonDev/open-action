"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.urlresolvers import reverse

from askbot.models import Post, User
from askbot.models.repute import Vote

from action import const, exceptions
from oa_notification.models import UserNotice
from action.tests import OpenActionViewTestCase, ActionViewTest

from lib import views_support

import os, urllib2


#class OpenActionViewTestCase(AskbotTestCase):
#
#    TEST_PASSWORD = "test"
#
#    def setUp(self):
#        """Alter table with new fields..."""
#        cu = connection.cursor()
#        f = file(os.path.join(
#            settings.PROJECT_ROOT,'askbot_extensions', 'sql', 'add_vote_referral.sql'
#        ), "r")
#        sql_initial = f.read()
#        f.close()
#        cu.execute(sql_initial)
#        cu.close()
#
#        # Create test user
#        username = 'user1'
#        self._author = self.create_user(username=username)
#
#        self._c = Client()
#
#    def create_user(self, *args, **kw):
#        """Make the user able to login."""
#        u = super(OpenActionViewTestCase, self).create_user(*args, **kw)
#        u.set_password(self.TEST_PASSWORD)
#        u.save()
#        return u
#
#    def create_user_unloggable(self, *args, **kw):
#        # Create user with no password --> cannot login
#        return super(OpenActionViewTestCase, self).create_user(*args, **kw)
#
#    def _create_action(self, owner=None, title="Test action #1"):
#
#        if not owner:
#            owner = self._author
#
#        # Create action to operate on
#        question = self.post_question(
#            user=self._author,
#            title=title
#        )
#        return question.thread.action 
#
#    def _logout(self):
#        self._c.logout()
#
#    def _login(self, user=None):
#        """Login a user.
#
#        If user is None, login the Action owner
#        """
#
#        self._logout()
#        login_user = [self._author, user][bool(user)]
#        rv = self._c.login(username=login_user.username, password=self.TEST_PASSWORD)
#        #KO: if not rv:
#        #KO:    raise Exception("Created user is not logged in")
#        return rv
#
#    def _check_for_error_response(self, response, e=Exception):
#        """HTTP response is always 200, context_data 'http_status_code' tells the truth"""
#        self.assertEqual(response.status_code, views_support.HTTP_SUCCESS)
#        self.assertEqual(
#            response.context_data['http_status_code'], 
#            views_support.HTTP_ERROR_INTERNAL
#        )
#        self.assertEqual(response.context_data['exception_type'], e)
#
#    def _check_for_success_response(self, response):
#        """HTTP response is always 200, context_data 'http_status_code' tells the truth"""
#        self.assertEqual(response.status_code, views_support.HTTP_SUCCESS)
#        self.assertEqual(
#            response.context_data['http_status_code'], 
#            views_support.HTTP_SUCCESS
#        )
#    
#    def _check_for_redirect_response(self,response, is_ajax=False):
#        """ HTTP response is 302, in case the server redirects to another page"""
#        if is_ajax:
#            self.assertEqual(response.status_code, views_support.HTTP_SUCCESS)
#            self.assertEqual(
#                response.context_data['http_status_code'], 
#                views_support.HTTP_REDIRECT
#            )
#        else:
#            self.assertEqual(response.status_code, views_support.HTTP_REDIRECT)

#---------------------------------------------------------------------------------

class OaNotificationTest(ActionViewTest):

#-----------------TESTS----------------------------------------------------------

    def test_notify_action_get_level_step(self):
        """ """
        # add voter to action voters
        self.test_add_vote_to_ready_action()
        # change status
        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        try:
            notice_obj = UserNotice.objects.get(user=self._author)
        except UserNotice.DoesNotExist as e:
            notice_obj = False

        self.assertTrue(notice_obj)
