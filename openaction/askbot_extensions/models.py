"""Some commodities extensions for Askbot models.

"""

from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver 
from django.conf import settings

from askbot.models import Thread, Vote, User, Post
from action import exceptions
from action_request import exceptions as action_request_exceptions
from action import const as action_const
from notification import models as notification
from friendship import models as friendship
from action_request.models import ActionRequest
from action_request import const as action_request_const
from organization.models import Organization
from lib.djangolib import ModelExtender
from lib import ClassProperty

from askbot_extensions import managers


#--------------------------------------------------------------------------------

class AskbotModelExtender(ModelExtender):

    ext_prefix = '_askbot_ext_'

#--------------------------------------------------------------------------------

class ThreadExtension(AskbotModelExtender):

    @property
    def _askbot_ext_question(self):
        return self._question_post()


Thread.add_to_class('ext_noattr', ThreadExtension())

#--------------------------------------------------------------------------------

class PostExtension(AskbotModelExtender):
 
    def _askbot_ext_is_comment_to_action(self):
        """ Check if the Post is a comment of a question.
        
        If the post is a question, self.get_parent_post()
        returns None anf an AttributeError has to be catched
        (the method will then return False)
        """
        rv = False
        # Use parent.is_question is OK because we are sure that parent is not None
        # (parent would be None if self.is_question())
        if self.is_comment() and self.parent.is_question():
            rv = True
        return rv 

    @property
    def _askbot_ext_action(self):
        """Encapsulation of action reference"""
        return self.thread.action

Post.add_to_class('ext_noattr', PostExtension())

#--------------------------------------------------------------------------------

#TODO: place can be blank/null at creation time?
#TODO TOTHINK User.add_to_class("place", models.CharField(max_length=512))

#--------------------------------------------------------------------------------

class VoteExtension(AskbotModelExtender):

    @property
    def _askbot_ext_action(self):
        """Encapsulation of action reference"""
        return self.voted_post.action

Vote.add_to_class('ext_noattr', VoteExtension())

Vote.add_to_class('referral', 
    models.ForeignKey(User, null=True, blank=True, help_text="voto suggerito da...")
)
Vote.add_to_class('is_anonymous', 
    models.BooleanField(default=False, help_text="visibile pubblicamente o no")
)
Vote.add_to_class('text', 
    models.TextField(default='',help_text="motivazione del voto")
)
Vote.add_to_class('objects', managers.VoteManager())

#--------------------------------------------------------------------------------
# Askbot signal handling

@receiver(pre_save, sender=Post)
def comment_check_before_save(sender, **kwargs):
    """ Overload Askbot.post.Post.save """

    post = kwargs['instance']
    
    #WAS: if not post.is_question():
    #WAS:     if post.thread.action.status in (
    #WAS:         action_const.ACTION_STATUS_DRAFT
    #WAS:     ):
    #WAS:         raise CommentActionInvalidStatusException(action_const.ACTION_STATUS_DRAFT)

    if post.is_comment():
        if post.action.status in (
            action_const.ACTION_STATUS_DRAFT,
            action_const.ACTION_STATUS_DELETED,
        ):
            raise exceptions.CommentActionInvalidStatusException(action_const.ACTION_STATUS_DRAFT)

    elif post.is_answer():
        if post.action.status in (
            action_const.ACTION_STATUS_DRAFT,
            action_const.ACTION_STATUS_DELETED,
        ):
            raise exceptions.BlogpostActionInvalidStatusException(action_const.ACTION_STATUS_DRAFT)
        

@receiver(pre_save, sender=Vote)
def vote_check_before_save(sender, **kwargs):
    """Overload Askbot.repute.Vote.save

    Check that a user cannot vote twice
    Check that referral cannot be the user himself
    """

    vote = kwargs['instance']

    #WAS "openaction style" 
    #WAS "openaction style"if vote.voted_post.post_type == 'question':
    #WAS "openaction style"    action = vote.voted_post.thread.action
    #WAS "openaction style"    
    #WAS "openaction style"    if action.get_vote_for_user(vote.user):
    #WAS "openaction style"        raise UserCannotVoteTwice(vote.user,vote.voted_post.thread.question)

    # Retrieve vote for the same user on the same post
    # Do it in "askbot style" in order to reuse code also for vote on comments

    #WAS COMMENT AAA: cannot vote twice is checked by Askbot
    #WAS try:
    #WAS     done_vote = vote.voted_post.votes.get(user=vote.user)
    #WAS except Post.DoesNotExist as e:
    #WAS     pass
    #WAS else:
    #WAS     if vote.pk != done_vote.pk:
    #WAS         # Check that we are not updating the same vote we have find
    #WAS         raise UserCannotVoteTwice(vote.user, vote.voted_post)

    # Check referral
    if vote.referral:
        if vote.referral == vote.user:
            raise exceptions.InvalidReferralError()

#---------------------------------------------------------------------------------


class UserExtension(AskbotModelExtender):

    @ClassProperty
    @classmethod
    def _askbot_ext_resource_type(cls):
        """String representation of resource type"""
        
        return cls.__name__.lower()

    @property
    def _askbot_ext_urn(self):
        """Unique resource name"""
        return '%s/%s' % (self.resource_type, self.pk)

    def _askbot_ext_assert_can_vote_action(self, action):
        """Check permission. If invalid --> raise exception"""
        # QUESTION: should an action which reached 'victory' status
        # still be votable?
        # ANSWER: no, it shouldn't
        if action.status not in (
            action_const.ACTION_STATUS_READY, 
            action_const.ACTION_STATUS_ACTIVE
        ):
            raise exceptions.VoteActionInvalidStatusException(action.status)

        return True

    def _askbot_ext_assert_can_vote_comment(self, comment):
        """Check permission. If invalid --> raise exception"""
        # CHECK THIS Matteo: shouldn't I be able to vote a comment
        # even if the Action cannot be voted ??
        try:
            self.assert_can_vote_action(comment.action)
        except exceptions.PermissionDenied as e:
            raise exceptions.VoteOnUnauthorizedCommentException()
            
        return True


    def _askbot_ext_assert_can_edit_action(self, action, attrs=None):
        """Check permission. If invalid --> raise exception.

        attrs can be a list of action attributes. 
        If some attr is specified do 'fine-grained' check,
        if attrs is None --> generic edit check.
        """

        def do_default_edit_action_check():
            if action.status not in (
                action_const.ACTION_STATUS_DRAFT, 
            ):
                raise exceptions.EditActionInvalidStatusException(action.status)
            elif action.question.author != self:
                #only action author can update it
                raise exceptions.UserIsNotActionOwnerException(self, action)
                

        if attrs:
            # NOTE: ... fine-grained check... let's see with OpenPolis if it is needed
            # FUTURE: maybe we can add some setting on "joining action" that
            # could give us some ability to change action even if is joined by
            # some users
            for attr in attrs:
                if attr == 'geoname_set':
                    #TODO
                    pass
                elif attr == 'politician_set':
                    #TODO
                    pass
                else:
                    do_default_edit_action_check()
        else:
            do_default_edit_action_check()

        return True

    def _askbot_ext_assert_can_create_blog_post(self, action):
        """Check permission. If invalid --> raise exception.
        
        Check if the user has the permission to add a new article to 
        the Action blog
        """
        if action.status in (
            action_const.ACTION_STATUS_DRAFT, 
            action_const.ACTION_STATUS_DELETED,
        ):
            raise exceptions.BlogpostActionInvalidStatusException(action.status)
        if self not in action.referrers.all():
            raise exceptions.UserIsNotActionReferralException(self, action)

    def _askbot_ext_assert_can_follow_action(self, action):
        """Check permission. If invalid --> raise exception"""
        if action.status in (
            action_const.ACTION_STATUS_DRAFT, 
            action_const.ACTION_STATUS_DELETED,
        ):
            raise exceptions.FollowActionInvalidStatusException(action.status)

        return True

    def _askbot_ext_assert_can_unfollow_action(self, action):
        """Check permission. If invalid --> raise exception"""
        if action.status in (
            action_const.ACTION_STATUS_DRAFT, 
            action_const.ACTION_STATUS_DELETED,
        ):
            raise exceptions.ParanoidException()
        elif not self.is_following_action(action):
            raise exceptions.ParanoidException()

        return True

    def _askbot_ext_assert_can_request_moderation_for_action(self, sender, recipient, action):
        """ Check permissions. If user is not action owner --> raise exception """
        if action.owner != sender:
            raise action_request_exceptions.RequestActionModerationNotOwnerException(sender, action)
        elif ActionRequest.objects.filter(recipient=recipient,
                action=action,
                request_type=action_request_const.REQUEST_TYPE['mod']
            ).count() >= settings.MAX_MODERATION_REQUESTS:
                raise action_request_exceptions.CannotRequestModerationToUser(sender, recipient, action)

        return True

    def _askbot_ext_assert_can_process_moderation_for_action(self, action_request, already_accepted):
        """ Check permissions. If user is not following action --> raise exception """
        followers = action_request.action.thread.followed_by.all()
        followers_not_moderators = followers.exclude(pk__in=action_request.action.moderator_set.all())
        if self not in followers_not_moderators and not already_accepted:
            raise action_request_exceptions.UserCannotModerateActionException(self, action_request.action)
        elif action_request.is_processed or action_request.request_type != action_request_const.REQUEST_TYPE['mod']:
            raise exceptions.ParanoidException()

        return True

    def _askbot_ext_check_moderation_response_already_answered(self, action_request):
        """ """

        return action_request.check_same_type_already_accepted()

        # LESSON: this method should not be here since it has nothing to do with "self"
        # read this LESSON and delete this method, changing the invoking code appropriately
        
        #KO: action_requests = ActionRequest.objects.filter(recipient=action_request.recipient,
        #KO:     action=action_request.action,
        #KO:     request_type=action_request_const.REQUEST_TYPE['mod']
        #KO: )

        #KO: for action_request in action_requests:
        #KO:     if action_request.is_accepted:
        #KO:         return True

        #KO: return False

#--------------------------------------------------------------------------------

    def _askbot_ext_follow_action(self, action):
        self.followed_threads.add(action.thread)

    def _askbot_ext_unfollow_action(self, action):
        self.followed_threads.remove(action.thread)

    def _askbot_ext_is_following_action(self, action):
        #WAS: return action.thread.followed_by.filter(id=self.id).exists() 
        return action.thread.is_followed_by(self)

    def _askbot_ext_friends(self):
        """Return User list of friendship friends (symmetric).

        TODO: return followers (asymmetric)"""

        symmetric_friends = friendship.Friend.objects.friends(user=self)
        # TODO: asymmetric_friends = friendship.Follow.objects.followers(user=self)
        return symmetric_friends

    @property
    def _askbot_ext_orgs_followed(self):
        #TODO Matteo rename in followed_orgs
        orgs_pk = self.orgmap_set.filter(is_follower=True).values_list('org__pk', flat=True)
        return Organization.objects.filter(pk__in=orgs_pk)

    @property
    def _askbot_ext_orgs_represented(self):
        #TODO Matteo rename in represented_orgs
        orgs_pk = self.orgmap_set.filter(is_representative=True).values_list('org__pk', flat=True)
        return Organization.objects.filter(pk__in=orgs_pk)


User.add_to_class('ext_noattr', UserExtension())



