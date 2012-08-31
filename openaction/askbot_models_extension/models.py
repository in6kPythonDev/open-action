"""Some commodities extensions for Askbot models.

"""

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from askbot.models import Thread, Vote, User
from action.exceptions import UserCannotVoteTwice,InvalidReferralError

from lib.djangolib import ModelExtender


#--------------------------------------------------------------------------------

class ThreadExtension(ModelExtender):

    ext_prefix = '_askbot_ext_'

    @property
    def _askbot_ext_question(self):
        return self._question_post()


Thread.add_to_class('thread_ext_noattr', ThreadExtension())

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

from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Vote)
def vote_check_before_save(sender, **kwargs):
    """Overload Askbot.repute.Vote.save

    TODO Matteo: Check that a user cannot vote twice
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
    try:
        done_vote = vote.voted_post.votes.get(user=vote.user)
    except ObjectDoesNotExist as e:
        pass
    else:
        raise UserCannotVoteTwice(vote.user, vote.voted_post)

    # Check referral
    if vote.referral:
        if vote.referral == vote.user:
            # TODO Matteo: define specific exception
            #WAS: raise PermissionDenied("Cannot be referred by yourself")
            raise InvalidReferralError()

