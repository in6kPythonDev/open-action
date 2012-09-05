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
from django.core.exceptions import PermissionDenied

from askbot.models import Post, User
from askbot.models.repute import Vote

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

        # Create test user
        username = 'user1'
        self._author = self.create_user(username=username)

        self._c = Client()

    def create_user(self, *args, **kw):
        """Make the user able to login."""
        u = super(OpenActionViewTestCase, self).create_user(*args, **kw)
        u.set_password(self.TEST_PASSWORD)
        u.save()
        return u

    def create_user_unloggable(self, *args, **kw):
        # Create user with no password --> cannot login
        return super(OpenActionViewTestCase, self).create_user(*args, **kw)

    def _create_action(self, owner=None, title="Test action #1"):

        if not owner:
            owner = self._author

        # Create action to operate on
        question = self.post_question(
            user=self._author,
            title=title
        )
        return question.thread.action 

    def _logout(self):
        self._c.logout()

    def _login(self, user=None):
        """Login a user.

        If user is None, login the Action owner
        """

        self._logout()
        login_user = [self._author, user][bool(user)]
        rv = self._c.login(username=login_user.username, password=self.TEST_PASSWORD)
        #KO: if not rv:
        #KO:    raise Exception("Created user is not logged in")
        return rv

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
    
    def _check_for_redirect_response(self,response):
        """ HTTP response is 302, in case the server redirects to another page"""
        self.assertEqual(response.status_code, views_support.HTTP_REDIRECT)
        

#---------------------------------------------------------------------------------

class ActionViewTest(OpenActionViewTestCase):
    """This class encapsulate tests for views."""

    def setUp(self):

        super(ActionViewTest, self).setUp()
        self._action = self._create_action()
        self.unloggable = self.create_user_unloggable("pluto")

    def _do_post_add_vote(self, query_string=""):

        response = self._c.post(
            reverse('action-vote-add', args=(self._action.pk,)) + \
            query_string
        )
        return response

    def _do_post_comment_add_vote(self, comment, **kwargs):

        response = self._c.post(
            reverse('comment-vote-add', args=(comment.pk,)),
            kwargs
        )
        return response
 
    def _do_post_add_comment(self, **kwargs):

        response = self._c.post(
            reverse('action-comment-add', args=(self._action.pk,)),
            kwargs
        )
        return response
    
    def _do_post_add_blog_post(self, **kwargs):

        response = self._c.post(
            reverse('action-blogpost-add', args=(self._action.pk,)),
            kwargs
        )
        #print response
        return response

    
    def _do_post_add_comment_to_blog_post(self, blog_post, **kwargs):

        response = self._c.post(
            reverse('blogpost-comment-add', args=(blog_post.pk,)),
            kwargs
        )
        return response

    def _do_post_create_action(self, **kwargs):

        response = self._c.post(
            reverse('action-create', args=()),
            kwargs
        )
        return response

    def _do_post_update_action(self, action, **kwargs):

        response = self._c.post(
            reverse('action-update', args=(action.pk,)),
            kwargs
        )
        return response

#------------------------------------------------------------------------------
    
    def test_add_vote_to_draft_action(self, user=None):

        self._action = self._create_action()

        # Test for authenticated user
        self._login(user)
        self._action.update_status(const.ACTION_STATUS_DRAFT)
        response = self._do_post_add_vote()

        # Error verified because invalid action status
        self._check_for_error_response(
            response, e=exceptions.VoteActionInvalidStatusException
        )

        action_voted = Action.objects.get(pk=self._action.pk)
        self.assertEqual(action_voted.score, self._action.score)

    def test_add_vote_to_ready_action(self, user=None, query_string=""):

        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        # Test for authenticated user
        self._login(user)

        response = self._do_post_add_vote(query_string=query_string)
        
        self._check_for_success_response(response)

        action_voted = Action.objects.get(pk=self._action.pk)
        self.assertEqual(action_voted.score, self._action.score+1)
        
    def test_add_vote_with_token(self):
        """Add a vote referenced by a user."""
        #print "--------------with_token" 

        self._action = self._create_action(title="Action vote with token")

        # Generate token for author
        token = self._action.get_token_for_user(self._author)
        query_string = "?token=%s" % token

        # Test that adding vote with logged user as referral fails
        self.assertRaises(
            Exception,
            self.test_add_vote_to_ready_action(query_string=query_string)
        )

        self.u2 = self.create_user(username='user2')
        self.test_add_vote_to_ready_action(
            user=self.u2, query_string=query_string
        )

        self.assertEqual(
            self._author, 
            self._action.get_vote_for_user(self.u2).referral
        )

    def test_not_add_two_votes_for_the_same_action(self):

        self._action = self._create_action(title="Action vote twice")
        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        # Test for authenticated user
        self._login()

        # First vote
        self._do_post_add_vote()

        # Second vote
        # Answer is HTTP so no assertRaises work here
        response = self._do_post_add_vote()
        self._check_for_error_response(response, e=exceptions.UserCannotVoteTwice)

#Matteo------------------------------------------------------------------------

    def test_add_comment_to_action(self, user=None):
 
        # Test for authenticated user
        logged_in = self._login(user)

        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        comment = "Ohi, che bel castello..."
    
        #Adding comment to action 
        response = self._do_post_add_comment(text=comment)
        #print "\n----------------add_comm_action resp: %s\n" % response

        if logged_in:
            # Success
            success = self._check_for_success_response(response)
            try:
                comment_obj = self._action.comments.get(
                    text=comment, author=self._author
                )
            except Post.DoesNotExist as e:
                comment_obj = False

            self.assertTrue(comment_obj)
            
        else:
            # Unauthenticated user cannot post
            self._check_for_redirect_response(response)

    def test_add_comment_to_draft_action(self, user=None):
 
        # Test for authenticated user
        logged_in = self._login(user)

        self._action.update_status(const.ACTION_STATUS_DRAFT)

        comment = "Ohi, che bel castello..."
    
        #Adding comment to action 
        response = self._do_post_add_comment(text=comment)
        #print "\n----------------add_comm_draft_action resp: %s\n" % response

        if logged_in:
            # cannot comment draft action
            self._check_for_error_response(response, 
                e = exceptions.CommentActionInvalidStatusException)
        else:
            # Unauthenticated user cannot post
            self._check_for_redirect_response(response)

    def test_unauthenticated_add_comment_to_action(self):
        #print "\n---------------unauthenticated\n"
        self.test_add_comment_to_action(user=self.unloggable)

    def test_add_blog_post_to_action(self, user=None):
        
        # test for authenticated user
        logged_in = self._login(user)
        
        #restore action status 
        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        #Adding blog_post to action 
        text = "Articolo di blog relativo a action %s" % self._action
        response = self._do_post_add_blog_post(text=text)
        #print "------------- %s" % response
        
        if logged_in:
            # Success
            success = self._check_for_success_response(response)
            try:
                blogpost_obj = self._action.blog_posts.get(
                    text=text, author=self._author
                )
            except Post.DoesNotExist as e:
                blogpost_obj = False

            self.assertTrue(blogpost_obj)
        else:
            # Unauthenticated user cannot post
            self._check_for_redirect_response(response)
    
    def test_unauthenticated_add_blog_post_to_action(self):
        #print "\n---------------unauthenticated\n"
        self.test_add_blog_post_to_action(user=self.unloggable)

    def test_add_comment_to_blog_post(self, user=None):

        # test for authenticated user. The user has to be authenticated
        # at this point since i need to add a post before commenting it
        #WAS: logged_in = self._login(user)
        self._login(self._author)

        #restore action status 
        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)
        #already tested, does not need asserts
        text = "Altro blog post su action %s" % self._action
        self._do_post_add_blog_post(text=text)
        blog_post = self._action.blog_posts.get(
            text=text, author=self._author
        )

        logged_in = self._login(user)

        comment_text = "... marcondiro ndiro ndello"
        
        #Adding comment to blog_post
        response = self._do_post_add_comment_to_blog_post(
            blog_post=blog_post,
            text=comment_text
        )
        #print response

        if logged_in:
            # Success
            success = self._check_for_success_response(response)
            try:
                comment_obj = blog_post.comments.get(
                    text=comment_text, author=self._author
                )
            except Post.DoesNotExist as e:
                comment_obj = False

            self.assertTrue(comment_obj)
            
        else:
            # Unauthenticated user cannot post
            self._check_for_redirect_response(response)

    def test_add_unauthenticated_comment_to_blog_post(self):
        #print "\n---------------unauthenticated\n"
        self.test_add_comment_to_blog_post(user=self.unloggable)

    def test_add_vote_to_action_comment(self, user=None):
        
        # Test for authenticated user
        self._login(self._author)

        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)
        
        comment_text = "Aggiungo dell'utente &s" % self._author
        
        #Adding comment to action
        response = self._do_post_add_comment(text=comment_text)
        comment = self._action.comments.get(text=comment_text,
            author=self._author
        )
        #print response

        logged_in = self._login(user)

        response = self._do_post_comment_add_vote(comment=comment)

        if logged_in:
            #Success
            self._check_for_success_response(response)
            try:
                vote_obj = comment.votes.get(user=self._author)
            except Vote.DoesNotExist as e:
                vote_obj = False

            self.assertTrue(vote_obj)
            
        else:
            # Unauthenticated user cannot post
            self._check_for_redirect_response(response)
                

    def test_add_unauthenticated_vote_to_action_comment(self):
        #print "\n---------------unauthenticated\n"
        self.test_add_vote_to_action_comment(user=self.unloggable)

    def test_not_add_two_votes_for_the_same_comment(self):

        # Test for authenticated user
        self._login()

        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        comment_text = "Aggiungo dell'utente &s" % self._author
        
        #Adding comment to action
        response = self._do_post_add_comment(text=comment_text)
        comment = self._action.comments.get(text=comment_text,
            author=self._author
        )
        #print response

        # First vote
        self._do_post_comment_add_vote(comment=comment)

        # Second vote
        # Answer is HTTP so no assertRaises work here
        response = self._do_post_comment_add_vote(comment=comment)
        self._check_for_error_response(response, e=exceptions.UserCannotVoteTwice)

    def test_create_action(self, user=None):

        logged_in = self._login(user)

        title = "Aggiungo una nuova action"
        tagnames = None
        text = "Blablablablablablabla" 

        response = self._do_post_create_action(title=title,
            tagnames=tagnames,
            text=text
        )
        #print "-------------------response: %s" % response

        if logged_in:
            self._check_for_success_response(response)

            try:
                action_obj = Action.objects.get(pk=1)
            except Action.DoesNotExist as e:
                action_obj = False

            self.assertTrue(action_obj)
        else:
            self._check_for_redirect_response(response)
        
    def test_update_action(self, user=None):

        logged_in = self._login(user)

        title = "Aggiungo una nuova action"
        tagnames = None
        text = "Blablablablablablabla" 

        #create action
        self._do_post_create_action(title=title,
            tagnames=tagnames,
            text=text
        )
        action = Action.objects.get(pk=1)
        #update action
        updated_text = "Gluglugluglugluglugluglu"
        response = self._do_post_update_action(action=action, 
            title=title,
            tags=tagnames,
            summary=None,
            text=updated_text
        ) 
        #print "-------------------response: %s" % response

        if logged_in:
            self._check_for_success_response(response)
            
            question_obj = action.question

            self.assertEqual(question_obj.text, updated_text)
        else:
            self._check_for_redirect_response(response)
        
