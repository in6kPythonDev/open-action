"""
This file holds tests for the action application
These will pass when you run "manage.py test".

"""

from django.test import TestCase
from askbot.tests.utils import AskbotTestCase

from django.test.client import Client
from django.db import connection

from django.conf import settings
from django.core.urlresolvers import reverse

from askbot.models import Post, User
from action.models import Action
from action import const, exceptions

from askbot_models_extension import models

from lib import views_support

import os

class OpenActionViewTestCase(AskbotTestCase):

    TEST_PASSWORD = "test"

    def setUp(self):
        """Alter table with new fields..."""
        cu = connection.cursor()
        f = file(os.path.join(
            settings.PROJECT_ROOT,'askbot_models_extension', 'sql', 'add_vote_referral.sql'
        ), "r")
        sql_initial = f.read()
        f.close()
        cu.execute(sql_initial)
        cu.close()

    def create_user(self, *args, **kw):
        """Make the user able to login."""
        u = super(OpenActionViewTestCase, self).create_user(*args, **kw)
        u.set_password(self.TEST_PASSWORD)
        u.save()
        return u

    def _create_action(self):

        # Create test user
        username = 'user1'
        self._author = self.create_user(username=username)

        # Create action to operate on
        self.__question = self.post_question(
            user=self._author,
            title="Test question #1"
        )
        self._action = self.__question.thread.action 

        self._c = Client()

    def _logout(self):
        self._c.logout()

    def _login(self, user=None):
        self._logout()
        login_user = [self._author, user][bool(user)]
        rv = self._c.login(username=login_user.username, password=self.TEST_PASSWORD)
        if not rv:
            raise Exception("Created user is not logged in")

    def _check_for_error_response(self, response, e=Exception):
        """HTTP response is always 200, context_data 'http_status_code' tells the truth"""
        self.assertEqual(response.status_code, views_support.HTTP_SUCCESS)
        self.assertEqual(
            response.context_data['http_status_code'], 
            views_support.HTTP_ERROR_INTERNAL
        )
        self.assertEqual(response.context_data['exception_type'], e)

    def _check_for_success_response(self, response):
        """HTTP response is always 200, context_data 'http_status_code' tells the truth"""
        self.assertEqual(response.status_code, views_support.HTTP_SUCCESS)
        self.assertEqual(
            response.context_data['http_status_code'], 
            views_support.HTTP_SUCCESS
        )


#---------------------------------------------------------------------------------

class ActionViewTest(OpenActionViewTestCase):
    """This class encapsulate tests for views."""

    def setUp(self):

        super(ActionViewTest, self).setUp()
        self._create_action()

    def __post_add_vote(self, query_string=""):

        response = self._c.post(
            reverse('action-vote-add', args=(self._action.pk,)) + \
            query_string
        )
        print response
        self.assertEqual(response.status_code, 200)
        return response

    def __comment_post_add_vote(self, query_string=""):

        response = self._c.post(
            reverse('comment-vote-add', args=(self._comment_post.pk,)) + \
            query_string
        )
        print response
        self.assertEqual(response.status_code, 200)
        return response
 
    def __post_add_comment(self, query_string=""):

        response = self._c.post(
            reverse('action-comment-add', args=(self._action.pk)) + \
            query_string
        )
        print response
        self.assertEqual(response.status_code, 200)
        return response
    
    def __post_add_blog_post(self, query_string=""):

        response = self._c.post(
            reverse('action-blogpost-add', args=(self._action.pk)) + \
            query_string
        )
        print response
        self.assertEqual(response.status_code, 200)
        return response

    
    def __blog_post_add_comment(self, query_string=""):

        response = self._c.post(
            reverse('blogpost-comment-add', args=(self._blog_post.pk)) + \
            query_string
        )
        print response
        self.assertEqual(response.status_code, 200)
        return response
    
    def test_add_vote_to_draft_action(self, user=None):

        # Test for authenticated user
        self._login(user)

        response = self.__post_add_vote()

        # Error verified because invalid action status
        self._check_for_error_response(
            response, e=exceptions.ActionInvalidStatusException
        )

        action_voted = Action.objects.get(pk=self._action.pk)
        self.assertEqual(action_voted.score, self._action.score)

    def test_add_vote_to_ready_action(self, user=None, query_string=""):

        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        # Test for authenticated user
        self._login(user)

        response = self.__post_add_vote(query_string=query_string)
        self._check_for_success_response(response)

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
            self.test_add_vote_to_ready_action(query_string=query_string)
        )

        self.u2 = self.create_user(username='user2')
        self.test_add_vote_to_ready_action(user=self.u2)

        self.assertEqual(
            self._author, 
            self._action.get_vote_for_user(self.u2).referra.referral
        )

    def test_not_add_two_votes_for_the_same_action(self):

        # First vote
        self.test_add_vote_to_ready_action()
        # Second vote
        # Answer is HTTP so no assertRaises work here
        response = self.test_add_vote_to_ready_action()

        self._check_for_error_response(response, e=UserCannotVoteTwice)

#Matteo------------------------------------------------------------------------

    def test_add_comment_to_action(self, user=None, query_string=""):
 
        # Test for authenticated user
        self._login(user)

        comment = "Ohi, che bel castello..."
        query_string = "?comment=%s" % comment
    
        #Adding comment to action 
        response = self.__post_add_comment(query_string=query_string)

        # Success
        success = self._check_for_success_response(response)

        if success:
            self._comment_post = self._action.comments.get(pk=1)

    def test_add_blog_post_to_action(self):
        
        # test for authenticated user
        self._login(user)
        
        #Adding blog_post to action 
        response = self.__post_add_blog_post()
        
        # Success
        success = self._check_for_success_response(response)

    def test_add_comment_to_blog_post(self):

        # test for authenticated user
        self._login(user)

        #Assuming that the previous test passed
        self.blog_post = self._action.blog_posts.get(pk=1)

        comment = "... marcondiro ndiro ndello"
        
        #Adding blog_post to action 
        response = self.__blog_post_add_comment(query_string="?comment=%s" % comment)

        # Success
        success = self._check_for_success_response(response)

    def test_add_vote_to_action_comment(self):
        
        # Test for authenticated user
        self._login(user)
        
        #Assuming that the previous test added a comment to the Action
        response = self.__comment_post_add_vote()

        #Success
        self._check_for_success_response(response)

