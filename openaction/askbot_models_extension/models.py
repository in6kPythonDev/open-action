"""Some commodities extensions for Askbot models.

"""

from django.db import models

from askbot.models import Thread, Vote, User

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
    TODO Matteo: Check that referral cannot be the user himself
    """

    vote = kwargs['instance']

    if vote.referral:
        if vote.referral == vote.user:
            # TODO Matteo: define specific exception
            raise PermissionDenied("Cannot be referred by yourself")

    # Retrieve vote for the same user on the same post
    # Maybe you could use the same code of Action.get_vote_referral_for_user
