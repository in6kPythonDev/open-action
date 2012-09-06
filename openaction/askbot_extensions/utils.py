from django.db import transaction
from action import exceptions
from askbot.models import Post

from django.conf import settings

import logging

log = logging.getLogger(settings.PROJECT_NAME)

@transaction.commit_on_success
def vote_add(askbot_post, user, referral=None):
    
    # Check that user cannot vote twice... 
    # Check that user != referral
    vote = user.upvote(askbot_post) 

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


