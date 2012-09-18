"""Some commodities extensions for Askbot models.

"""

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver 

from askbot.models import Thread, Vote, User, Post
from action import exceptions 
from action import const as action_cons
from notification import models as notification

from lib.djangolib import ModelExtender


#--------------------------------------------------------------------------------

class ThreadExtension(ModelExtender):

    ext_prefix = '_askbot_ext_'

    @property
    def _askbot_ext_question(self):
        return self._question_post()


Thread.add_to_class('ext_noattr', ThreadExtension())

#--------------------------------------------------------------------------------

class PostExtension(ModelExtender):
    pass

    
#TODO TOTHINK if we could enlarge even the summary field...

#--------------------------------------------------------------------------------

#TODO: place can be blank/null at creation time?
#TODO TOTHINK User.add_to_class("place", models.CharField(max_length=512))

#--------------------------------------------------------------------------------

Vote.add_to_class('referral', 
    models.ForeignKey(User, null=True, blank=True)
)

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
    #WAS:         #DONE Matteo: define appropriate arguments
    #WAS:         raise CommentActionInvalidStatusException(action_const.ACTION_STATUS_DRAFT)

    if post.is_comment():
        if post.thread.action.status in (
            action_const.ACTION_STATUS_DRAFT,
            action_const.ACTION_STATUS.deleted,
        ):
            raise exceptions.CommentActionInvalidStatusException(action_const.ACTION_STATUS_DRAFT)

    elif post.is_answer():
        if post.thread.action.status in (
            action_const.ACTION_STATUS_DRAFT,
            action_const.ACTION_STATUS.deleted,
        ):
            raise BlogpostActionInvalidStatusException(action_const.ACTION_STATUS_DRAFT)
        

@receiver(pre_save, sender=Vote)
def vote_check_before_save(sender, **kwargs):
    """Overload Askbot.repute.Vote.save

    DONE Matteo: Check that a user cannot vote twice
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
            # TODO Matteo: define specific exception
            #WAS: raise PermissionDenied("Cannot be referred by yourself")
            raise exceptions.InvalidReferralError()

@receiver(pre_save, sender=User)
def user_set_notice_settings(sender, **kwargs):
 
    user = kwargs['instance']

    #default is openaction backend
    if user.is_active:
        notification.get_notification_setting(user=user,
            notice_type=,
            medium="default"
        )

#---------------------------------------------------------------------------------


class UserExtension(ModelExtender):

    ext_prefix = '_askbot_ext_'

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
            self.assert_can_vote_action(comment.thread.action)
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
            # CHECK THIS Matteo: can the moderators edit an Action ??
            # (and, in the case, which parts of it?) 
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
            action_const.ACTION_STATUS.deleted,
        ):
            raise exceptions.BlogpostActionInvalidStatusException(action.status)
        if self not in action.referrers.all():
            raise exceptions.UserIsNotActionReferralException(self, action)

    def _askbot_ext_assert_can_follow_action(self, action):
        """Check permission. If invalid --> raise exception"""
        if action.status in (
            action_const.ACTION_STATUS_DRAFT, 
            action_const.ACTION_STATUS.deleted,
        ):
            raise exceptions.FollowActionInvalidStatusException(action.status)

        return True

    def _askbot_ext_assert_can_unfollow_action(self, action):
        """Check permission. If invalid --> raise exception"""
        if action.status in (
            action_const.ACTION_STATUS_DRAFT, 
            action_const.ACTION_STATUS.deleted,
        ):
            raise exceptions.ParanoidException()
        elif not self.is_following(action):
            raise exceptions.ParanoidException()

        return True

    def _askbot_ext_follow_action(self, action=None):
        self.followed_threads.add(action.thread)

    def _askbot_ext_unfollow_action(self, action=None):
        self.followed_threads.remove(action.thread)

    def _askbot_ext_is_following_action(self, action=None):
        #WAS: return action.thread.followed_by.filter(id=self.id).exists() 
        return action.thread.is_followed_by(self)

User.add_to_class('ext_noattr', UserExtension())



