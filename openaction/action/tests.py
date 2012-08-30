"""
This file holds tests for the action application
These will pass when you run "manage.py test".

"""

from django.test import TestCase
from askbot.tests.utils import AskbotTestCase

from django.test.client import Client

from django.conf import settings

from askbot.models import Post
from action.models import Action

class OpenActionViewTestCase(AskbotTestCase):

    def _create_action(self):

        # Create test user
        username = 'user1'
        self._author = self.create_user(username=username)

        # Create action to operate on
        self.__question = self.post_question(user=self._author)
        self._action = self.__question.thread.action 

        self._c = Client()


    def _get_test_password(self, user):
        # Not used now
        return settings.TEST_PASSWORDS.get(user.username,'')

    def _logout(self):
        self._c.logout()

    def _login(self, user=None):
        self._logout()
        if user:
            login_user = user
        else:
            login_user = self._author
        self._c.login(username=login_user.username, password=self._get_test_password(login_user))

class ActionViewTest(OpenActionViewTestCase):
    """This class encapsulate tests for views."""

    def setUp(self):

        self._create_action()

    def test_add_vote(self, query_string=""):

        # Test for authenticated user
        self._login()

        response = self._c.post(
            reverse('action-vote-add', pk=self._action.pk) + query_string
        )
        self.assertEqual(response.status_code, 200)
        action_voted = Action.objects.get(pk=self._action.pk)
        self.assertEqual(action_voted.score, self._action.score+1)
        
    def test_add_vote_with_token(self):
        """Add a vote referenced by a user."""

        # Generate token for author
        token = self._action.get_token_for_user(self._author)
        query_string = "?token=%s" % token

        # Test that adding vote with logged user as referral fails
        self.assertRaises(
            Exception,
            self.test_add_vote(query_string=query_string)
        )

        self.u2 = self.create_user(username='user2')
        self._login(u2)

        response = self._c.post(
            reverse('action-vote-add', pk=self._action.pk) + query_string
        )

        self.assertEqual(
            self._author, 
            self._action.get_vote_referral_for_user(self.u2)
        )

