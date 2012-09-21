from django.db import transaction
from action import exceptions
from askbot.models import Post

from django.conf import settings

import logging

log = logging.getLogger(settings.PROJECT_NAME)

@transaction.commit_on_success
def vote_add(askbot_post, user, referral=None):
    
    # Vote and set referral if needed
    # Check that user cannot vote twice... 
    # Check that user != referral

    # TODOFUTURE: if we would like to add in_nomine_org vote, we could do it here
    # being aware that:
    # * the first time the User can vote (and we can set in_nomine_org like we do with referral)
    # * the second time the User cannot vote (and we can force voting)
    # * the third time a Vote.MultipleObjectsReturned will be raised 
    #

    log.debug("Vado a votare il post %s" % askbot_post)
    vote = user.upvote(askbot_post) 
    log.debug("Risposta da upvote %s" % vote)

    if vote:

        # Add referral
        vote.referral = referral
        vote.save()

        log.debug("Vote added for user %s on post %s with referral %s" % (
            user, askbot_post, referral
        ))
    else:
        log.debug("Vote NOT added for user %s on post %s with referral %s" % (
            user, askbot_post, referral
        ))
        try:
            assert askbot_post.votes.get(user=user)
        except Post.DoesNotExist as e:
            raise exceptions.UserCannotVote(user, askbot_post)
        else:
            raise exceptions.UserCannotVoteTwice(user, askbot_post)


