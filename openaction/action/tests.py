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

from notification.models import Notice 

from action.models import Action, Geoname
from action import const, exceptions

from askbot_extensions import models

from lib import views_support

import os, urllib2

class OpenActionViewTestCase(AskbotTestCase):

    TEST_PASSWORD = "test"

    def setUp(self):
        # Matteo: this shouldn't be necessary anymore
        #WAS: """Alter table with new fields..."""
        #WAS: cu = connection.cursor()
        #WAS: f = file(os.path.join(
        #WAS:     settings.PROJECT_ROOT,'askbot_extensions', 'sql', 'add_vote_referral.sql'
        #WAS: ), "r")
        #WAS: sql_initial = f.read()
        #WAS: f.close()
        #WAS: cu.execute(sql_initial)
        #WAS: cu.close()

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
        return question.action 

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
    
    def _check_for_redirect_response(self,response, is_ajax=False):
        """ HTTP response is 302, in case the server redirects to another page"""
        if is_ajax:
            self.assertEqual(response.status_code, views_support.HTTP_SUCCESS)
            self.assertEqual(
                response.context_data['http_status_code'], 
                views_support.HTTP_REDIRECT
            )
        else:
            self.assertEqual(response.status_code, views_support.HTTP_REDIRECT)

#---------------------------------------------------------------------------------

class ActionViewTest(OpenActionViewTestCase):
    """This class encapsulate tests for views."""

    def setUp(self):

        super(ActionViewTest, self).setUp()
        self._action = self._create_action()
        self.unloggable = self.create_user_unloggable("pluto")

    def _post(self, url, is_ajax, **kwargs):
        
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

    def _do_post_action_add_vote(self, action, query_string="", ajax=False):

        response = self._post(
            reverse('action-vote-add', args=(action.pk,)) + \
            query_string,
            ajax
        )
        return response

    def _do_post_comment_add_vote(self, comment, ajax=False, **kwargs):

        response = self._post(
            reverse('comment-vote-add', args=(comment.pk,)),
            ajax,
            **kwargs
        )
        return response
 
    def _do_post_add_comment(self, ajax=False, **kwargs):

        response = self._post(
            reverse('action-comment-add', args=(self._action.pk,)),
            ajax,
            **kwargs
        )
        return response
    
    def _do_post_add_blog_post(self, ajax=False, **kwargs):

        response = self._post(
            reverse('action-blogpost-add', args=(self._action.pk,)),
            ajax,
            **kwargs
        )
        return response

    
    def _do_post_add_comment_to_blog_post(self, blog_post, ajax=False, **kwargs):

        response = self._post(
            reverse('blogpost-comment-add', args=(blog_post.pk,)),
            ajax,
            **kwargs
        )
        return response

    def _do_post_create_action(self, ajax=False, **kwargs):

        response = self._post(
            reverse('action-create', args=()),
            ajax,
            **kwargs
        )
        return response

    def _do_post_update_action(self, action, ajax=False, **kwargs):

        response = self._post(
            reverse('action-update', args=(action.pk,)),
            ajax,
            **kwargs
        )
        return response

    def _do_post_follow_action(self, action, ajax=False, **kwargs):
        
        response = self._post(
            reverse('action-follow', args=(action.pk,)),
            ajax,
            **kwargs
        )
        return response

    def _do_post_unfollow_action(self, action, ajax=False, **kwargs):

        response = self._post(
            reverse('action-unfollow', args=(action.pk,)),
            ajax,
            **kwargs
        )
        return response

    def _create_geoname(self, pk, name, kind):

        Geoname.objects.get_or_create(pk=pk,
            name=name,
            kind=kind 
        )

    def _test_edit_set(self, geoname_set, updated_geoname_set, user=None, **kwargs):

        title = "Aggiungo una nuova action"
        tagnames = None
        text = "Blablablablablablabla"

        #geoname_set = geoname_set

        #create action
        r = self._do_post_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text,
            geoname_set=geoname_set
        )
        #print "-------------------response_create: %s" % r
        action = Action.objects.latest()

        logged_in = self._login(user)
        #update action
        updated_text = "Gluglugluglugluglugluglu"
        #updated_geoname_set = updated_geoname_set

        response = self._do_post_update_action( 
            action=action,
            ajax=True,
            title=title,
            tags=tagnames,
            summary=None,
            text=updated_text,
            geoname_set=updated_geoname_set
        ) 
        #print "\n\n\nTest with old geo_names: %s and new geo_names: %s . Response: %s" % (geoname_set, updated_geoname_set, response)

        if logged_in:
            self._check_for_redirect_response(response, is_ajax=True)
    
            geoname_list = []
            question_obj = action.question

            self.assertEqual(question_obj.text, updated_text)
            for obj in action.geoname_set.all():
                geoname_list.append(obj.pk)
            geoname_list.sort()
            #geoname_set = action.geoname_set.all()
            self.assertEqual(updated_geoname_set, geoname_list)
        else:
            self._check_for_redirect_response(response)

#------------------------------------------------------------------------------
    
    def test_add_vote_to_draft_action(self, user=None):

        self._action = self._create_action(title="action_vote")

        # Test for authenticated user
        self._login(user)
        self._action.update_status(const.ACTION_STATUS_DRAFT)
        response = self._do_post_action_add_vote(self._action, ajax=True)

        # Error verified because invalid action status
        self._check_for_error_response(
            response, e=exceptions.VoteActionInvalidStatusException
        )

        action_voted = Action.objects.get(pk=self._action.pk)
        self.assertEqual(action_voted.score, self._action.score)

    def test_add_vote_to_ready_action_user_equal_to_referral(self, user=None, query_string="", action=None):
        """ Try to add a vote to an Action in a ready status with
        the voting user equal to the referral
        """

        if not action:
            self._action = self._create_action()
        else:
            self._action = action
        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        # Test for authenticated user
        self._login(user)

        response = self._do_post_action_add_vote(self._action, 
            query_string=query_string,
            ajax=True
        )
        print "\ntest_add_vote_to_ready_action %s\n" % response
        print "\nSELF ACTION SCORE:   %s \n" % self._action.score

        self._check_for_error_response(response, e=exceptions.InvalidReferralError)
        action_voted = Action.objects.get(pk=self._action.pk)
        self.assertEqual(action_voted.score, self._action.score+1)

    def test_add_vote_to_ready_action(self, user=None, query_string="", action=None):
        """ Add a vote to an Action in a ready status """ 
        if not action:
            self._action = self._create_action()
        else:
            self._action = action
        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        # Test for authenticated user
        self._login(user)

        response = self._do_post_action_add_vote(self._action, 
            query_string=query_string,
            ajax=True
        )
        print "\ntest_add_vote_to_ready_action %s\n" % response

        self._check_for_success_response(response)
        action_voted = Action.objects.get(pk=self._action.pk)
        self.assertEqual(action_voted.score, self._action.score+1)
        voters = action_voted.voters
        print "\n\nVOTERSs: %s" % voters
        self.assertTrue([self._author, user][bool(user)] in voters)
        
    def test_add_vote_with_token(self):
        """Add a vote referenced by a user."""
        #print "--------------with_token" 

        self._action = self._create_action(title="Action vote with token")

        print "\nSELF ACTION SCORE:   %s \n" % self._action.score

        # Generate token for author
        token = self._action.get_token_for_user(self._author)
        query_string = "?ref_token=%s" % urllib2.quote(token)

        print "\nQS: %s\n" % query_string 

        # Test that adding vote with logged user as referral raise exception (however, a vote is still added
        self.assertRaises(
            exceptions.InvalidReferralError,
            self.test_add_vote_to_ready_action_user_equal_to_referral(query_string=query_string, action=self._action)
        )

        self.u2 = self.create_user(username='user2')
        self.test_add_vote_to_ready_action(
            user=self.u2, query_string=query_string
        )

        self.assertEqual(
            self._author, 
            self._action.get_vote_for_user(self.u2).referral
        )
        
        action_voted = Action.objects.get(pk=self._action.pk)
        #two votes added
        self.assertEqual(action_voted.score, self._action.score+2)

    def test_not_add_two_votes_to_the_same_action(self):

        self._action = self._create_action(title="Action vote twice")
        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        # Test for authenticated user
        self._login()

        # First vote
        self._do_post_action_add_vote(self._action, ajax=True)

        # Second vote
        # Answer is HTTP so no assertRaises work here
        response = self._do_post_action_add_vote(self._action, ajax=True)
        print "test_not_add_two_votes_to_the_same_action: %s" % response

        self._check_for_error_response(response, e=exceptions.UserCannotVoteTwice)

        action_voted = Action.objects.get(pk=self._action.pk)
        self.assertEqual(action_voted.score, self._action.score)
#Matteo------------------------------------------------------------------------

    def test_add_comment_to_action(self, user=None):
 
        # Test for authenticated user
        logged_in = self._login(user)

        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        comment = "Ohi, che bel castello..."
    
        #Adding comment to action 
        response = self._do_post_add_comment(ajax=True, text=comment)
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
        response = self._do_post_add_comment(ajax=True, text=comment)
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
        response = self._do_post_add_blog_post(ajax=True, text=text)
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
        self._login()

        #restore action status 
        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)
        #already tested, does not need asserts
        text = "Altro blog post su action %s" % self._action
        self._do_post_add_blog_post(ajax=True, text=text)
        blog_post = self._action.blog_posts.get(
            text=text, author=self._author
        )

        logged_in = self._login(user)

        comment_text = "... marcondiro ndiro ndello"
        #Adding comment to blog_post
        response = self._do_post_add_comment_to_blog_post(
            ajax=True,
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
        self._login()

        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)
        
        comment_text = "Aggiungo voto dell'utente %s" % self._author
        
        #Adding comment to action
        response = self._do_post_add_comment(ajax=True, text=comment_text)
        comment = self._action.comments.get(text=comment_text,
            author=self._author
        )
        print "add_vote_action_comment_response: %s" % response

        logged_in = self._login(user)

        response = self._do_post_comment_add_vote(ajax=True, comment=comment)

        if logged_in:
            #Success
            self._check_for_success_response(response)
            try:
                vote_obj = comment.votes.get(user=self._author)
            except Vote.DoesNotExist as e:
                vote_obj = False

            self.assertTrue(vote_obj)

            comment_voted = Post.objects.get(pk=comment.pk)
            self.assertEqual(comment_voted.score, comment.score+1)
            
        else:
            # Unauthenticated user cannot post
            self._check_for_redirect_response(response)
            comment_voted = Post.objects.get(pk=comment.pk)
            self.assertEqual(comment_voted.score, comment.score)
                

    def test_add_unauthenticated_vote_to_action_comment(self):
        #print "\n---------------unauthenticated\n"
        self.test_add_vote_to_action_comment(user=self.unloggable)

    def test_not_add_two_votes_to_the_same_comment(self):

        # Test for authenticated user
        self._login()

        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        comment_text = "Aggiungo dell'utente %s" % self._author
        
        #Adding comment to action
        response = self._do_post_add_comment(ajax=True, text=comment_text)
        comment = self._action.comments.get(text=comment_text,
            author=self._author
        )
        print "not_add_to_votes_to_same_comment: %s" % response

        # First vote
        self._do_post_comment_add_vote(ajax=True, comment=comment)
        comment_voted = Post.objects.get(pk=comment.pk)
        print "\n\n c_v.score %s, c.score %s" % (comment_voted.score, comment.score+1)
        self.assertEqual(comment_voted.score, comment.score+1)

        old_score = comment_voted.score
        # Second vote
        # Answer is HTTP so no assertRaises work here
        response = self._do_post_comment_add_vote(ajax=True, comment=comment)
        self._check_for_error_response(response, e=exceptions.UserCannotVoteTwice)
        comment_voted = Post.objects.get(pk=comment.pk)
        #WAS: self.assertEqual(comment_voted.score, comment.score)
        self.assertEqual(comment_voted.score, old_score)

    def test_create_action(self, user=None):

        logged_in = self._login(user)

        title = "Aggiungo una nuova action"
        tagnames = None
        text = "Blablablablablablabla" 

        response = self._do_post_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text
        )
        #print "-------------------response: %s" % response

        if logged_in:
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                #action_obj = Action.objects.get(pk=1)
                action_obj = Action.objects.latest()
            except Action.DoesNotExist as e:
                action_obj = False

            self.assertTrue(action_obj)
        else:
            self._check_for_redirect_response(response)
        
    def test_create_unauthenticated_action(self):
        #print "unauthenticated"
        self.test_create_action(user=self.unloggable)

    
    def create_test_geonames(self):

        self._login()

#        title = "Aggiungo una nuova action"
#        tagnames = None
#        text = "Blablablablablablabla"
#        #Create geonames
        self._create_geoname(pk=1, 
            name='Italia', 
            kind='Stato'
        )
        self._create_geoname(pk=2, 
            name='Ancona', 
            kind='Provincia'
	    )
        self._create_geoname(pk=3, 
            name='Fabriano', 
            kind='Comune'
        )
        self._create_geoname(pk=4, 
            name='Macerata', 
            kind='Provincia'
	    )
        self._create_geoname(pk=5, 
            name='Camerino', 
            kind='Comune'
        )

        for geo in Geoname.objects.all():
            print "geo: %s" % geo.id


    def test_update_action_add_geonames(self, user=None):

        self._login()
        self.create_test_geonames()

        #TEST #1
        self._test_edit_set([1], [1,2], user) 

    def test_update_action_remove_geonames(self, user=None):

        self._login()
        self.create_test_geonames()
        #TEST #2
        self._test_edit_set([1,2,3], [1,2], user) 

    def test_update_action_same_geonames(self, user=None):

        self._login()
        self.create_test_geonames()
        #TEST #3
        self._test_edit_set([1,2], [1,2], user) 

    def test_update_action_not_overlapping_geonames(self, user=None):

        self._login()
        self.create_test_geonames()
        #TEST #4
        self._test_edit_set([1,3,5], [2,4], user) 

#    def test_update_unauthenticated_action(self):
#        #print "unauthenticated"
#        self.test_update_action(user=self.unloggable)
    
    def test_update_not_draft_action(self):

        self._login()

        title = "Aggiungo una nuova action"
        tagnames = None
        text = "Blablablablablablabla" 

        #create action
        r = self._do_post_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text
        )
        #print "-------------------response: %s" % r
        action = Action.objects.latest()
        
        action.compute_threshold()
        action.update_status(const.ACTION_STATUS_READY)

        #update action
        updated_text = "Gluglugluglugluglugluglu"
        response = self._do_post_update_action(
            action=action, 
            ajax=True,
            title=title,
            tags=tagnames,
            summary=None,
            text=updated_text
        ) 
        #print "-------------------response: %s" % response

        self._check_for_error_response(response,
            exceptions.EditActionInvalidStatusException
        )

    def test_update_action_user_is_not_author(self):

        self._login()

        title = "Aggiungo una nuova action"
        tagnames = None
        text = "Blablablablablablabla" 

        #create action
        r = self._do_post_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text
        )
        #print "-------------------response: %s" % r
        action = Action.objects.latest()
        
        # a user from the one who created the action tries to update it
        user2 = self.create_user(username='user2')
        self._login(user2)

        #update action
        updated_text = "Gluglugluglugluglugluglu"
        response = self._do_post_update_action(
            action=action, 
            ajax=True,
            title=title,
            tags=tagnames,
            summary=None,
            text=updated_text
        ) 
        #print "-------------------response: %s" % response

        self._check_for_error_response(response,
            exceptions.UserIsNotActionOwnerException
        )

    def test_follow_action(self, user=None):
        
        logged_in = self._login(user)
        
        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        response = self._do_post_follow_action(
            action=self._action,
            ajax=True
        )
        #print "-------------------response: %s" % response

        if logged_in:
            #success
            self._check_for_success_response(response)
            #check that user is following action
            login_user = [self._author, user][bool(user)]
            self.assertTrue(login_user.is_following_action(self._action))
        else:
            self._check_for_redirect_response(response)

    def test_follow_draft_action(self, user=None):
        
        logged_in = self._login(user)
        
        self._action.update_status(const.ACTION_STATUS_DRAFT)

        response = self._do_post_follow_action(
            action=self._action,
            ajax=True
        )
        #print "-------------------response: %s" % response

        if logged_in:
            self._check_for_error_response(response, e=exceptions.FollowActionInvalidStatusException)
            #check that user is not following action
            login_user = [self._author, user][bool(user)]
            self.assertTrue(login_user.is_following_action(self._action) == False)
        else:
            self._check_for_redirect_response(response)

    def test_unfollow_action(self, user=None):
        
        logged_in = self._login(user)
        
        self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)
        
        response = self._do_post_follow_action(
            action=self._action,
            ajax=True
        )
        self._check_for_success_response(response)

        response = self._do_post_unfollow_action(
            action=self._action,
            ajax=True
        )
        print "-------------------unfollow_response: %s" % response

        if logged_in:
            #success
            self._check_for_success_response(response)
            #check that user is following action
            login_user = [self._author, user][bool(user)]
            self.assertTrue(login_user.is_following_action(self._action) == False)
        else:
            self._check_for_redirect_response(response)

    def test_unfollow_draft_action(self, user=None):
        """ this is an illegal situation, draft action 
            should not be followed from beginning with 
        """
        logged_in = self._login(user)
        
        self._action.update_status(const.ACTION_STATUS_DRAFT)

        response = self._do_post_unfollow_action(
            action=self._action,
            ajax=True
        )
        print "-------------------unfollow_draft_response: %s" % response

        if logged_in:
            self._check_for_error_response(response, e=exceptions.ParanoidException)
            #check that user is not following action
            login_user = [self._author, user][bool(user)]
            self.assertTrue(login_user.is_following_action(self._action) == False)
        else:
            self._check_for_redirect_response(response)

#--------------------------------------------------------------------------------

#class ViewTest(OpenActionViewTestCase):
#    """This class encapsulate tests for views."""
#
#    def setUp(self):
#
#        super(ActionViewTest, self).setUp()
#        self.unloggable = self.create_user_unloggable("pluto")
#
#    def _post(self, url, is_ajax, **kwargs):
#        
#        if is_ajax:
#            response = self._c.post(url,
#                kwargs,
#                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
#            )
#        else:
#            response = self._c.post(url,
#                kwargs
#            )
#        return response

from notification.models import *

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
 
    def _post(self, url, is_ajax, **kwargs):
        
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
    
    def _get(self, url, is_ajax, **kwargs):
        
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

    def _do_post_notice_settings(self, ajax=False):

        response = self._post(
            reverse('notification_notice_settings', args=()),
            ajax
        )
        return response

    def _do_get_notice_settings(self, ajax=False):

        response = self._get(
            reverse('notification_notice_settings', args=()),
            ajax
        )
        return response

    def test_notice_settings(self):

        self._login()

        response = self._do_post_notice_settings(ajax=True)

        print "POST response status code %s" % response.status_code
        print "POST response content %s" % response.content

        response = self._do_get_notice_settings(ajax=True)

        print "GET response status code %s" % response.status_code
        print "GET response content %s" % response.content
