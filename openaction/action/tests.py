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
from organization.models import Organization, UserOrgMap

from action.models import Action, Geoname, Politician
from action import const, exceptions
from action.signals import post_action_status_update
from oa_notification.handlers import register_status_update_activity
from askbot_extensions import consts as ae_consts
from oa_notification import models as oa_notification
from external_resource.models import ExternalResource
from ajax_select import get_lookup

from askbot_extensions import models

from lib import views_support

import os, urllib2, datetime

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
    
    def _create_organization(self, name, external_resource=None):
        org, created = Organization.objects.get_or_create(name=name)
        return org


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

    def _check_for_success_response(self, response, is_ajax=True):
        """HTTP response is always 200, context_data 'http_status_code' tells the truth"""
        if is_ajax:
            self.assertEqual(response.status_code, views_support.HTTP_SUCCESS)
            self.assertEqual(
                response.context_data['http_status_code'], 
                views_support.HTTP_SUCCESS
            )
        else:
            self.assertEqual(response.status_code, views_support.HTTP_SUCCESS)
    
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
        #Manually create notice types
        oa_notification.create_notice_types("","","")

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

    def _do_GET_action_details(self, action, ajax=False):

        response = self._GET(
            reverse('action-detail', args=(action.pk,)),
            ajax
        )
        return response

    def _do_POST_action_add_vote(self, action, query_string="", ajax=False):

        response = self._POST(
            reverse('action-vote-add', args=(action.pk,)) + \
            query_string,
            ajax
        )
        return response

    def _do_POST_comment_add_vote(self, comment, ajax=False, **kwargs):

        response = self._POST(
            reverse('comment-vote-add', args=(comment.pk,)),
            ajax,
            **kwargs
        )
        return response
 
    def _do_POST_add_comment(self, ajax=False, **kwargs):

        response = self._POST(
            reverse('action-comment-add', args=(self._action.pk,)),
            ajax,
            **kwargs
        )
        return response
    
    def _do_POST_add_blog_POST(self, ajax=False, **kwargs):

        response = self._POST(
            reverse('action-blogpost-add', args=(self._action.pk,)),
            ajax,
            **kwargs
        )
        return response

    
    def _do_POST_add_comment_to_blog_POST(self, blog_post, ajax=False, **kwargs):

        response = self._POST(
            reverse('blogpost-comment-add', args=(blog_post.pk,)),
            ajax,
            **kwargs
        )
        return response

    def _do_POST_create_action(self, ajax=False, **kwargs):

        response = self._POST(
            reverse('action-create', args=()),
            ajax,
            **kwargs
        )
        return response

    def _do_POST_update_action(self, action, ajax=False, **kwargs):

        response = self._POST(
            reverse('action-update', args=(action.pk,)),
            ajax,
            **kwargs
        )
        return response

    def _do_POST_follow_action(self, action, ajax=False, **kwargs):
        
        response = self._POST(
            reverse('action-follow', args=(action.pk,)),
            ajax,
            **kwargs
        )
        return response

    def _do_POST_unfollow_action(self, action, ajax=False, **kwargs):

        response = self._POST(
            reverse('action-unfollow', args=(action.pk,)),
            ajax,
            **kwargs
        )
        return response

    #WAS: def _do_GET_filter_actions_by_geoname(self, geoname_ext_res_id, ajax=False, **kwargs):
    def _do_GET_filter_actions(self, ajax=False, **kwargs):

        response = self._GET(
            reverse('actions-filter', args=()),#args=(geoname_ext_res_id,)),
            ajax,
            **kwargs
        )
        return response

    def _test_edit_set(self, model, user=None, **kwargs):

        if model == Geoname:
            old_ids = kwargs['geoname_set'][1:-1].split('|')
            geoname_set = kwargs['geoname_set']
            updated_set = kwargs['updated_geoname_set']
            updated_ids = [int(_id) for _id in  updated_set[1:-1].split('|')] 
        elif model == Politician:
            #old_ids = kwargs['politician_set'][1:-1].split('|')
            old_ids = kwargs['old_politician_set'][1:-1].split('|')
            geoname_set = kwargs['geoname_set']
            politician_set = kwargs['politician_set']
            updated_set = kwargs['updated_politician_set']
            updated_set_ids = kwargs['updated_politician_ids']
            updated_ids = [int(_id) for _id in  updated_set_ids[1:-1].split('|')] 
            
        #updated_ids = [int(_id) for _id in  updated_set[1:-1].split('|')] 
        
        logged_in = self._login(user)

        title = "Aggiungo una nuova action"
        tagnames = None
        text = "Blablablablablablabla" 
        in_nomine = "%s-%s" % ("user", [self._author, user][bool(user)].pk)
        threshold = 0

        if model == Geoname:
            response = self._do_POST_create_action(
                ajax=True,
                title=title,
                tagnames=tagnames,
                text=text,
                in_nomine=in_nomine,
                geoname_set=geoname_set,
                threshold=threshold
            )
        elif model == Politician:
            response = self._do_POST_create_action(
                ajax=True,
                title=title,
                tagnames=tagnames,
                text=text,
                in_nomine=in_nomine,
                geoname_set=geoname_set,
                politician_set=politician_set,
                threshold=threshold
            )
        print "________________________response_create: %s" % response

        if logged_in:
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                #action_obj = Action.objects.get(pk=1)
                action_obj = Action.objects.latest()
            except Action.DoesNotExist as e:
                action_obj = False

            self.assertTrue(action_obj)

            #checck that the action is not in nomine of any association,
            # since the user is not representative of any ot them
            self.assertTrue(action_obj.in_nomine_org == None)
            #TODO: check that Action has the desired locations
            for _id in old_ids:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    _obj = model.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    _obj = False

                self.assertTrue(_obj)
        else:
            self._check_for_redirect_response(response)

        action = Action.objects.latest()

        #update action
        updated_text = "Gluglugluglugluglugluglu"

        if model == Geoname:
            response = self._do_POST_update_action( 
                action=action,
                ajax=True,
                title=title,
                tags=tagnames,
                text=updated_text,
                in_nomine=in_nomine,
                geoname_set=updated_set,
                threshold=threshold
            )
        elif model == Politician:
            response = self._do_POST_update_action( 
                action=action,
                ajax=True,
                title=title,
                tags=tagnames,
                text=updated_text,
                in_nomine=in_nomine,
                geoname_set=geoname_set,
                politician_set=updated_set,
                threshold=threshold
            ) 
        print "-------------------response: %s" % response

        if logged_in:
            self._check_for_redirect_response(response, is_ajax=True)
    
            _list = []
            question_obj = action.question

            self.assertEqual(question_obj.text, updated_text)
            if model == Geoname:
                for obj in action.geoname_set.all():
                    _list.append(int(obj.external_resource.ext_res_id))
            if model == Politician:
                for obj in action.politician_set.all():
                    _list.append(int(obj.external_resource.ext_res_id))
            updated_ids.sort()
            _list.sort()
            #geoname_set = action.geoname_set.all()
            #geoname_list_ids = "|" + "|".join( str(pk) for pk in geoname_list ) + "|"
            self.assertEqual(updated_ids, _list)
        else:
            self._check_for_redirect_response(response)

#------------------------------------------------------------------------------

    def test_cannot_set_ready_status_to_action_without_title(self):

        self._action = self._create_action(title="")

        try:
            self._action.update_status(const.ACTION_STATUS_READY)
        except exceptions.ThresholdNotComputableException as e:
            expected_exception = e
        except e:
            expected_exception = False

        self.assertTrue(expected_exception)
            

    def test_add_vote_to_draft_action(self, user=None):

        self._action = self._create_action(title="action_vote")

        # Test for authenticated user
        self._login(user)
        self._action.update_status(const.ACTION_STATUS_DRAFT)
        response = self._do_POST_action_add_vote(self._action, ajax=True)

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
        #self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        # Test for authenticated user
        self._login(user)

        if not query_string:
            # Generate token for author
            token = self._action.get_token_for_user([self._author, user][bool(user)])
            query_string = "?ref_token=%s" % urllib2.quote(token)

        response = self._do_POST_action_add_vote(self._action, 
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
        #self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        # Test for authenticated user
        self._login(user)

        response = self._do_POST_action_add_vote(self._action, 
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
        #self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        # Test for authenticated user
        self._login()

        # First vote
        self._do_POST_action_add_vote(self._action, ajax=True)

        # Second vote
        # Answer is HTTP so no assertRaises work here
        response = self._do_POST_action_add_vote(self._action, ajax=True)
        print "test_not_add_two_votes_to_the_same_action: %s" % response

        self._check_for_error_response(response, e=exceptions.UserCannotVoteTwice)

        action_voted = Action.objects.get(pk=self._action.pk)
        self.assertEqual(action_voted.score, self._action.score)
#Matteo------------------------------------------------------------------------

    def test_add_comment_to_action(self, user=None):
 
        # Test for authenticated user
        logged_in = self._login(user)

        #self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        comment = "Ohi, che bel castello..."
    
        #Adding comment to action 
        response = self._do_POST_add_comment(ajax=True, text=comment)
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
        response = self._do_POST_add_comment(ajax=True, text=comment)
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
        #self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        #Adding blog_post to action 
        text = "Articolo di blog relativo a action %s" % self._action
        response = self._do_POST_add_blog_POST(ajax=True, text=text)
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

    def test_add_comment_to_blog_POST(self, user=None):

        # test for authenticated user. The user has to be authenticated
        # at this point since i need to add a post before commenting it
        #WAS: logged_in = self._login(user)
        self._login()

        #restore action status 
        #self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)
        #already tested, does not need asserts
        text = "Altro blog post su action %s" % self._action
        self._do_POST_add_blog_POST(ajax=True, text=text)
        blog_post = self._action.blog_posts.get(
            text=text, author=self._author
        )

        logged_in = self._login(user)

        comment_text = "... marcondiro ndiro ndello"
        #Adding comment to blog_post
        response = self._do_POST_add_comment_to_blog_POST(
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

    def test_add_unauthenticated_comment_to_blog_POST(self):
        #print "\n---------------unauthenticated\n"
        self.test_add_comment_to_blog_POST(user=self.unloggable)

    def test_add_vote_to_action_comment(self, user=None):
        
        # Test for authenticated user
        self._login()

        #self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)
        
        comment_text = "Aggiungo voto dell'utente %s" % self._author
        
        #Adding comment to action
        response = self._do_POST_add_comment(ajax=True, text=comment_text)
        comment = self._action.comments.get(text=comment_text,
            author=self._author
        )
        print "add_vote_action_comment_response: %s" % response

        logged_in = self._login(user)

        response = self._do_POST_comment_add_vote(ajax=True, comment=comment)

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

        #self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        comment_text = "Aggiungo dell'utente %s" % self._author
        
        #Adding comment to action
        response = self._do_POST_add_comment(ajax=True, text=comment_text)
        comment = self._action.comments.get(text=comment_text,
            author=self._author
        )
        print "not_add_to_votes_to_same_comment: %s" % response

        # First vote
        self._do_POST_comment_add_vote(ajax=True, comment=comment)
        comment_voted = Post.objects.get(pk=comment.pk)
        print "\n\n c_v.score %s, c.score %s" % (comment_voted.score, comment.score+1)
        self.assertEqual(comment_voted.score, comment.score+1)

        # Second vote
        # Answer is HTTP so no assertRaises work here
        response = self._do_POST_comment_add_vote(ajax=True, comment=comment)
        self._check_for_error_response(response, e=exceptions.UserCannotVoteTwice)
        comment_voted = Post.objects.get(pk=comment.pk)
        self.assertEqual(comment_voted.score, comment.score+1)

    def test_create_action(self, user=None):

        logged_in = self._login(user)

        title = "Aggiungo una nuova action"
        tagnames = None
        text = "Blablablablablablabla" 
        geoname_set = '|145|185|287|', 
        in_nomine = "%s-%s" % ("user", [self._author, user][bool(user)].pk)
        threshold = 0

        response = self._do_POST_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text,
            geoname_set=geoname_set, 
            in_nomine=in_nomine,
            threshold=threshold
        )
        print "-------------------response: %s" % response

        if logged_in:
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                #action_obj = Action.objects.get(pk=1)
                action_obj = Action.objects.latest()
            except Action.DoesNotExist as e:
                action_obj = False

            self.assertTrue(action_obj)

            #check that the action is not in nomine of any association,
            # since the user is not representative of any ot them
            self.assertTrue(action_obj.in_nomine_org == None)
        else:
            self._check_for_redirect_response(response)
 
    def test_create_action_with_locations(self, user=None):

        logged_in = self._login(user)

        title = "Aggiungo una nuova action"
        tagnames = None
        text = "Blablablablablablabla" 
        in_nomine = "%s-%s" % ("user", [self._author, user][bool(user)].pk)
        geoname_set = '|145|185|287|'
        threshold = 0

        response = self._do_POST_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text,
            in_nomine=in_nomine,
            geoname_set=geoname_set,
            threshold=threshold
        )
        print "-------------------response: %s" % response

        if logged_in:
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                #action_obj = Action.objects.get(pk=1)
                action_obj = Action.objects.latest()
            except Action.DoesNotExist as e:
                action_obj = False

            self.assertTrue(action_obj)

            #checck that the action is not in nomine of any association,
            # since the user is not representative of any ot them
            self.assertTrue(action_obj.in_nomine_org == None)
            #TODO: check that Action has the desired locations
            for _id in [145,185,287]:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    geoname_obj = Geoname.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    geoname_obj = False

                self.assertTrue(geoname_obj)
        else:
            self._check_for_redirect_response(response)

    def test_create_action_with_politicians(self, user=None):

        logged_in = self._login(user)

        title = "Aggiungo una nuova action"
        tagnames = None
        text = "Blablablablablablabla" 
        in_nomine = "%s-%s" % ("user", [self._author, user][bool(user)].pk)
          
        #geoname_set = '|145|185|287|'
        geoname_set = '|5132|1974|', 
        #politician_set = '|332997|543662|626209|'
        politician_set = '|355786|397514|583733|583732|391934|391931|',
        #politician_set = '|332997|543662|626222|'
        threshold = "0"

        response = self._do_POST_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text,
            in_nomine=in_nomine,
            geoname_set=geoname_set,
            politician_set=politician_set,
            threshold=threshold
        )
        print "-------------------response: %s" % response

        if logged_in:
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                #action_obj = Action.objects.get(pk=1)
                action_obj = Action.objects.latest()
            except Action.DoesNotExist as e:
                action_obj = False

            self.assertTrue(action_obj)

            #checck that the action is not in nomine of any association,
            # since the user is not representative of any ot them
            self.assertTrue(action_obj.in_nomine_org == None)
            #TODO: check that Action has the desired locations
            #for _id in [145,185,287]:
            for _id in [5132,1974]:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    geoname_obj = Geoname.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    geoname_obj = False

                self.assertTrue(geoname_obj)
            #check that the politicians have been created
            #for _id in [332997,543662,626222]:
            for _id in [125719,397513,740,583731,274820,21]:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    politician_obj = Politician.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    politician_obj = False

                self.assertTrue(politician_obj)
 
        else:
            self._check_for_redirect_response(response)

    def test_create_unauthenticated_action(self):
        #print "unauthenticated"
        self.test_create_action(user=self.unloggable)

    def test_create_action_in_nomine_of_association(self, user=None):
        logged_in = self._login(user)
        organization = self._create_organization(name="org")

        title = "Aggiungo una nuova action in nomine di un'associazione"
        tagnames = None
        geoname_set = '|145|185|287|', 
        text = "Blablablablablablabla"
        threshold = 0
        in_nomine = "%s-%s" % ("org", organization.pk)

        # NOT DRY: This post is implemented in organization.tests.
        # At this point, it could be better to collect all the utility
        # functions (such as the POST and GET functions, that are 
        # useful in more than one TestClass) togheter in class from 
        # which all the other TestClass will inherit
        
        #WAS: response = self._POST(
        #WAS:     reverse('org-user-represent', args=(organization.pk,)),
        #WAS:     True
        #WAS: )
        ############HACK
        org = organization
        user = [self._author, user][bool(user)]

        mapping, created = UserOrgMap.objects.get_or_create(user=user,
            org=org,
            is_representative=True
        )
        #############
        
        #if logged_in:
        #    self._check_for_success_response(response)
        #else:
        #    self._check_for_redirect_response(response)

        response = self._do_POST_create_action(
            ajax=True,
            title=title,
            geoname_set=geoname_set, 
            tagnames=tagnames,
            text=text,
            threshold=threshold,
            in_nomine=in_nomine
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

            self.assertTrue(
                organization in [self._author, user][bool(user)].represented_orgs
            )

        else:
            self._check_for_redirect_response(response)

    #def create_test_geonames(self):

    #    self._login()

    #     title = "Aggiungo una nuova action"
    #     tagnames = None
    #     text = "Blablablablablablabla"
    #     #Create geonames
    #    self._create_geoname(pk=1, 
    #        name='Italia', 
    #        kind='Stato',
    #    )
    #    self._create_geoname(pk=2, 
    #        name='Ancona', 
    #        kind='Provincia'
	#    )
    #    self._create_geoname(pk=3, 
    #        name='Fabriano', 
    #        kind='Comune'
    #    )
    #    self._create_geoname(pk=4, 
    #        name='Macerata', 
    #        kind='Provincia'
	#    )
    #    self._create_geoname(pk=5, 
    #        name='Camerino', 
    #        kind='Comune'
    #    )

    #    for geo in Geoname.objects.all():
    #        print "geo: %s" % geo.id

    def test_update_action_add_geonames(self, user=None):

        self._login()

        #TEST #1
        self._test_edit_set(Geoname, 
            user,
            #geoname_set = '|145|185|' 
            geoname_set = '|5132|1974|',
            #updated_geoname_set = '|145|185|287|'
            updated_geoname_set = '|5132|1974|145|',
        ) 

    def test_update_action_add_politicians(self, user=None):

        self._login()

        #TEST #1
        self._test_edit_set(Politician, 
            user, 
            #geoname_set = '|145|185|287|',
            geoname_set = '|5132|1974|', 
            #politician_set = '|332997|543662|',
            politician_set = '|355786|397514|',
            old_politician_set = '|125719|397513|',
            #updated_politician_set = '|332997|543662|626209|'
            updated_politician_set = '|624417|333080|498067|',
            updated_politician_ids = '|274713|333079|4521|'
        ) 

    def test_update_action_remove_geonames(self, user=None):

        self._login()

        #TEST #2
        self._test_edit_set(Geoname, 
            user, 
            #geoname_set = '|145|185|287|',
            geoname_set = '|5132|1974|',
            #updated_geoname_set = '|145|185|'
            updated_geoname_set = '|5132|',
        ) 

    def test_update_action_remove_politicians(self, user=None):

        self._login()

        #TEST #2
        self._test_edit_set(Politician, 
            user, 
            #geoname_set = '|145|185|287|', 
            geoname_set = '|5132|1974|',
            #politician_set = '|332997|543662|626209|',
            politician_set = '|355786|397514|583733|',
            old_politician_set = '|125719|397513|740|',
            updated_politician_set = '|355786|397514|',
            updated_politician_ids = '|125719|397513|'
        ) 

    def test_update_action_same_geonames(self, user=None):

        self._login()

        #TEST #3
        self._test_edit_set(Geoname, 
            user, 
            #geoname_set = '|145|185|287|',
            geoname_set = '|5132|1974|',
            #updated_geoname_set = '|145|185|287|'
            updated_geoname_set = '|5132|1974|',
        ) 

    def test_update_action_same_politicians(self, user=None):

        self._login()

        #TEST #3
        self._test_edit_set(Politician, 
            user, 
            #geoname_set = '|145|185|287|', 
            geoname_set = '|5132|1974|',
            #politician_set = '|332997|543662|626209|',
            politician_set = '|355786|397514|583733|',
            old_politician_set = '|125719|397513|740|',
            #updated_politician_set = '|332997|543662|626209|'
            updated_politician_set = '|355786|397514|583733|',
            updated_politician_ids = '|125719|397513|740|'
        ) 

    def test_update_action_not_overlapping_geonames(self, user=None):

        self._login()

        #TEST #4
        self._test_edit_set(Geoname, 
            user, 
            geoname_set = '|145|287|',
            updated_geoname_set = '|185|'
        ) 

    def test_update_action_not_overlapping_politicians(self, user=None):

        self._login()

        #TEST #4
        self._test_edit_set(Politician, 
            user, 
            #geoname_set = '|145|185|287|', 
            geoname_set = '|5132|1974|',
            #politician_set = '|332997|543662|626209|',
            politician_set = '|355786|397514|583733|',
            old_politician_set = '|125719|397513|740|',
            updated_politician_set = '|583733|',
            updated_politician_ids = '|740|'
        ) 

#    def test_update_unauthenticated_action(self):
#        #print "unauthenticated"
#        self.test_update_action(user=self.unloggable)
    
    def test_update_not_draft_action(self):

        self._login()

        title = "Aggiungo una nuova action"
        tagnames = None
        geoname_set = '|145|185|287|', 
        text = "Blablablablablablabla"
        in_nomine = "%s-%s" % ("user", self._author.pk)
        threshold = 0;

        #create action
        r = self._do_POST_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text,
            in_nomine=in_nomine,
            geoname_set=geoname_set,
            threshold=threshold
        )
        #print "-------------------response: %s" % r
        action = Action.objects.latest()
        
        action.compute_threshold()
        action.update_status(const.ACTION_STATUS_READY)

        #update action
        updated_text = "Gluglugluglugluglugluglu"
        response = self._do_POST_update_action(
            action=action, 
            ajax=True,
            title=title,
            tags=tagnames,
            summary=None,
            text=updated_text,
            #geoname_set=geoname_set, 
            threshold=threshold,
            in_nomine=in_nomine
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
        in_nomine = "%s-%s" % ("user", self._author.pk)
        geoname_set = '|145|185|287|', 
        threshold = 0
        #create action

        r = self._do_POST_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text,
            in_nomine=in_nomine,
            geoname_set=geoname_set, 
            threshold = threshold
        )
        #print "-------------------response: %s" % r
        action = Action.objects.latest()
        
        # a user from the one who created the action tries to update it
        user2 = self.create_user(username='user2')
        self._login(user2)

        in_nomine = "%s-%s" % ("user", user2.pk)

        #update action
        updated_text = "Gluglugluglugluglugluglu"
        response = self._do_POST_update_action(
            action=action, 
            ajax=True,
            title=title,
            tags=tagnames,
            summary=None,
            text=updated_text,
            #geoname_set=geoname_set, 
            threshold = threshold,
            in_nomine=in_nomine
        ) 
        #print "-------------------response: %s" % response

        self._check_for_error_response(response,
            exceptions.UserIsNotActionOwnerException
        )

    def test_follow_action(self, user=None):
        
        logged_in = self._login(user)
        
        #self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)

        response = self._do_POST_follow_action(
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

        response = self._do_POST_follow_action(
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
        
        #self._action.compute_threshold()
        self._action.update_status(const.ACTION_STATUS_READY)
        
        response = self._do_POST_follow_action(
            action=self._action,
            ajax=True
        )
        self._check_for_success_response(response)

        response = self._do_POST_unfollow_action(
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

        response = self._do_POST_unfollow_action(
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

    def test_filter_actions_by_geoname(self, user=None):
        """ Filter action by geoname, then order the resulting QS"""

        #self.test_create_action_with_locations(user)
        logged_in = self._login(user)

        #CREATING FIRST ACTION
        title = "Aggiungo una nuova action"
        tagnames = None
        text = "Blablablablablablabla" 
        in_nomine = "%s-%s" % ("user", [self._author, user][bool(user)].pk)
        geoname_set = '|145|185|287|'
        threshold = 0

        response = self._do_POST_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text,
            in_nomine=in_nomine,
            geoname_set=geoname_set,
            threshold=threshold
        )

        if logged_in:
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                #action_obj = Action.objects.get(pk=1)
                action_obj = Action.objects.latest()
            except Action.DoesNotExist as e:
                action_obj = False

            self.assertTrue(action_obj)

            self.assertTrue(action_obj.in_nomine_org == None)
            for _id in [145,185,287]:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    geoname_obj = Geoname.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    geoname_obj = False

                self.assertTrue(geoname_obj)
        else:
            self._check_for_redirect_response(response)

        #VOTING FIRST ACTION
        action_obj.update_status(const.ACTION_STATUS_READY)

        response = self._do_POST_action_add_vote(action_obj, 
            ajax=True
        )

        self._check_for_success_response(response)
        action_voted = Action.objects.get(pk=action_obj.pk)
        self.assertEqual(action_voted.score,action_obj.score+1)
        voters = action_voted.voters
        self.assertTrue([self._author, user][bool(user)] in voters)

        #CREATING SECOND ACTION       
        title = "Aggiungo una seconda action"
        tagnames = None
        text = "Blablablablablablabla" 
        in_nomine = "%s-%s" % ("user", [self._author, user][bool(user)].pk)
        geoname_set = '|145|'
        threshold = 0

        response = self._do_POST_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text,
            in_nomine=in_nomine,
            geoname_set=geoname_set,
            threshold=threshold
        )

        if logged_in:
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                #action_obj = Action.objects.get(pk=1)
                action_obj = Action.objects.latest()
            except Action.DoesNotExist as e:
                action_obj = False

            self.assertTrue(action_obj)

            self.assertTrue(action_obj.in_nomine_org == None)
            for _id in [145]:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    geoname_obj = Geoname.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    geoname_obj = False

                self.assertTrue(geoname_obj)
        else:
            self._check_for_redirect_response(response)

        #TEST FILTERING
        geo_pks = "1"
        sort="popular"

        response = self._do_GET_filter_actions(
            ajax=True,
            geo_pks=geo_pks,
            sort=sort
        )

        self._check_for_success_response(response)

    def test_filter_actions_by_politician(self, user=None):
        """ Filter action by politician, then order the resulting QS"""

        pol_pks = "1"
        sort="popular"

        #TODO
        self.test_create_action_with_locations(user)
        self.test_create_action_with_politicians(user)

        response = self._do_GET_filter_actions(
            ajax=True,
            pol_ext_res_id=pol_pks,
            sort=sort
        )

        self._check_for_success_response(response)

    def test_filter_actions_by_geoname_and_politician(self, user=None):
        """ Filter action by geoname and politician, then order the 
        resulting QS
        """

        #self.test_create_action_with_politicians(user)
        logged_in = self._login(user)

        #CREATING FIRST ACTION
        title = "Aggiungo una nuova action"
        tagnames = None
        text = "Blablablablablablabla" 
        in_nomine = "%s-%s" % ("user", [self._author, user][bool(user)].pk)
        geoname_set = '|145|185|287|'
        politician_set = '|657159|'
        threshold = "0"

        response = self._do_POST_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text,
            in_nomine=in_nomine,
            geoname_set=geoname_set,
            politician_set=politician_set,
            threshold=threshold
        )

        if logged_in:
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                action_obj = Action.objects.latest()
            except Action.DoesNotExist as e:
                action_obj = False

            self.assertTrue(action_obj)

            self.assertTrue(action_obj.in_nomine_org == None)
            #TODO: check that Action has the desired locations
            for _id in [145,185,287]:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    geoname_obj = Geoname.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    geoname_obj = False

                self.assertTrue(geoname_obj)
            for _id in [657157]:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    politician_obj = Politician.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    politician_obj = False

                self.assertTrue(politician_obj)
 
        else:
            self._check_for_redirect_response(response)

        #CREATING SECOND ACTION
        title = "Aggiungo una seconda action"
        tagnames = None
        text = "Blablablablablablabla" 
        in_nomine = "%s-%s" % ("user", [self._author, user][bool(user)].pk)
        #geoname_set = '|145|185|287|'
        geoname_set = '|5132|1974|',
        #politician_set = '|332997|543662|626222|'
        politician_set = '|355786|397514|583733|'
        threshold = "0"

        response = self._do_POST_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text,
            in_nomine=in_nomine,
            geoname_set=geoname_set,
            politician_set=politician_set,
            threshold=threshold
        )

        if logged_in:
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                action_obj = Action.objects.latest()
            except Action.DoesNotExist as e:
                action_obj = False

            self.assertTrue(action_obj)

            self.assertTrue(action_obj.in_nomine_org == None)
            #TODO: check that Action has the desired locations
            for _id in [145,185,287]:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    geoname_obj = Geoname.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    geoname_obj = False

                self.assertTrue(geoname_obj)
            #for _id in [332997,543662,626222]:
            for _id in [125719,397513,740]:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    politician_obj = Politician.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    politician_obj = False

                self.assertTrue(politician_obj)
 
        else:
            self._check_for_redirect_response(response)

        #FILTER ACTION
        pol_pks = "1"
        geo_pks = "1"
        sort="politicians"

        response = self._do_GET_filter_actions(
            ajax=True,
            pol_pks=pol_pks,
            geo_pks=geo_pks,
            sort=sort
        )

        self._check_for_success_response(response)

    def test_sort_actions(self, user=None):
        """ Order actions by 
        * `hot`: number of votes in a certain period of time
        * `popular`: number of votes
        * `date`: descending
        """

        #self.test_create_action_with_politicians(user)
        logged_in = self._login(user)

        #CREATING FIRST ACTION
        title = "Aggiungo una nuova action"
        tagnames = None
        text = "Blablablablablablabla" 
        in_nomine = "%s-%s" % ("user", [self._author, user][bool(user)].pk)
        geoname_set = '|145|185|287|'
        politician_set = '|657159|'
        threshold = "0"

        response = self._do_POST_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text,
            in_nomine=in_nomine,
            geoname_set=geoname_set,
            politician_set=politician_set,
            threshold=threshold
        )

        if logged_in:
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                action_obj = Action.objects.latest()
            except Action.DoesNotExist as e:
                action_obj = False

            self.assertTrue(action_obj)

            self.assertTrue(action_obj.in_nomine_org == None)
            #TODO: check that Action has the desired locations
            for _id in [145,185,287]:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    geoname_obj = Geoname.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    geoname_obj = False

                self.assertTrue(geoname_obj)
            for _id in [657157]:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    politician_obj = Politician.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    politician_obj = False

                self.assertTrue(politician_obj)
 
        else:
            self._check_for_redirect_response(response)

        #CREATING SECOND ACTION
        title = "Aggiungo una seconda action"
        tagnames = None
        text = "Blablablablablablabla" 
        in_nomine = "%s-%s" % ("user", [self._author, user][bool(user)].pk)
        #geoname_set = '|145|185|287|'
        geoname_set = '|5132|1974|',
        #politician_set = '|332997|543662|626222|'
        politician_set = '|355786|397514|583733|'
        threshold = "0"

        response = self._do_POST_create_action(
            ajax=True,
            title=title,
            tagnames=tagnames,
            text=text,
            in_nomine=in_nomine,
            geoname_set=geoname_set,
            politician_set=politician_set,
            threshold=threshold
        )

        if logged_in:
            self._check_for_redirect_response(response, is_ajax=True)

            try:
                action_obj = Action.objects.latest()
            except Action.DoesNotExist as e:
                action_obj = False

            self.assertTrue(action_obj)

            self.assertTrue(action_obj.in_nomine_org == None)
            #TODO: check that Action has the desired locations
            for _id in [145,185,287]:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    geoname_obj = Geoname.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    geoname_obj = False

                self.assertTrue(geoname_obj)
            #for _id in [332997,543662,626222]:
            for _id in [125719,397513,740]:
                try:
                    e_r = ExternalResource.objects.get(ext_res_id=_id)
                    politician_obj = Politician.objects.get(external_resource=e_r)
                except Action.DoesNotExist as e:
                    politician_obj = False

                self.assertTrue(politician_obj)
 
        else:
            self._check_for_redirect_response(response)

        #VOTING SECOND ACTION

        self._do_POST_action_add_vote(action_obj)

        #FILTER ACTION
        pol_pks = "1"
        geo_pks = "1"
        sort="politicians"

        #SORT ACTION BY HOT
        __sort = "hot:7"

        response = self._do_GET_filter_actions(
            ajax=True,
            pol_pks=pol_pks,
            geo_pks=geo_pks,
            sort=sort,
            __sort=__sort
        )

        self._check_for_success_response(response)

        #SORT ACTION BY POPULARITY

        __sort = "popular"

        response = self._do_GET_filter_actions(
            ajax=True,
            pol_pks=pol_pks,
            geo_pks=geo_pks,
            sort=sort,
            __sort=__sort
        )

        self._check_for_success_response(response)

        #SORT ACTION BY DATE

        __sort = "date"

        response = self._do_GET_filter_actions(
            ajax=True,
            pol_pks=pol_pks,
            geo_pks=geo_pks,
            sort=sort,
            __sort=__sort
        )

        self._check_for_success_response(response)

    def test_action_details(self, user=None):
        """ Show Action details, including data on its politicians 
            and locations  
        """

        action = self._create_action(title="see_action_detail")

        # Test for authenticated user
        logged_in = self._login(user)
        action.update_status(const.ACTION_STATUS_DRAFT)

        if logged_in:
            response = self._do_GET_action_details(action)
            self._check_for_success_response(response, is_ajax=False)

            action.update_status(const.ACTION_STATUS_READY)

            response = self._do_GET_action_details(action)
            self._check_for_success_response(response, is_ajax=False)

            self._do_POST_action_add_vote(action)

            response = self._do_GET_action_details(action)
            #print("response: %s" % response)
            self._check_for_success_response(response, is_ajax=False)

    def test_action_remaining_votes_to_threshold(self, user=None):
        """ See how many votes remain to hit the threshold """

        action = self._create_action(title="remaining_votes_to_threshold")

        # Test for authenticated user
        logged_in = self._login(user)
        action.update_status(const.ACTION_STATUS_DRAFT)

        if logged_in:
            #try:
            #    action.votes_to_threshold
            #    raise_exception = False
            #except exceptions.ThresholdNotComputableException as e:
            #    raise_exception = True
            #self.assertTrue(raise_exception)

            self.assertEqual(action.votes_to_threshold, 3)

            action.update_status(const.ACTION_STATUS_READY)
 
            self._do_POST_action_add_vote(action)

            self.assertEqual(action.votes_to_threshold, 2)
