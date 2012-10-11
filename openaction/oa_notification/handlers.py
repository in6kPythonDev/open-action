from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.urlresolvers import reverse

from askbot.models import Post, User
from askbot.models.repute import Vote
from askbot.models.user import Activity
from notification import models as notification
from action.models import Action
from action.signals import (post_action_status_update, 
    post_declared_vote_add, action_moderator_removed 
)
from action_request.signals import (action_moderation_request_submitted, 
    action_moderation_request_processed, 
    action_message_sent, 
    action_message_replied
)

from action_request.models import ActionRequest
from action_request import consts as ar_consts
from oa_notification import consts as notification_consts
from action import const as action_consts
from askbot_extensions import consts as ae_consts

import logging

log = logging.getLogger(settings.PROJECT_NAME)


@receiver(post_save, sender=Post)
def notify_add_blog_post(sender, **kwargs):
    """ Notify to Action referrers and followers that a new post 
    has been added to the Action blog

    #1 set the recipients (the receivers)
    #2 send notification(notification.send)
    
    Possible options:
    * 'now=True and queue=True': error
    * 'now=True and queue=False': send notice immediately by passing 'now=True' to 
    send function
    * 'queue=True and now=False': queue the notice in order to send it later
    * 'now=False and queue=False'(default): let the default notification 
    configuration decide

    QUESTION: should we pass the referrer who created the blog post as the 
    sender of the notice (in sender=)?
    ANSWER: no, the sender is always "the system"
    """

    if kwargs['created']:
        post = kwargs['instance']

        # This is a generic Post post_save handler, 
        # so we have to check if it is an answer
        if post.is_answer():

            action = post.action

            referrers = action.referrers
            #WAS: followers = action.thread.followed_by.all()
            followers = action.followers
            # recipients
            users = referrers | followers

            extra_context = ({
                "blog_post" : post,
                "action" : action
            })

            notification.send(users=users, 
                label=notification_consts.ACTION_MAKE_BLOGPOST, 
                extra_context=extra_context, 
                on_site=True, 
                sender=None, 
                now=True
            )

#WAS: @receiver(post_save, sender=Vote)
@receiver(post_declared_vote_add, sender=Vote)
def notify_user_join_your_action(sender, **kwargs):
    """ Notify to the users who woted an Action that 
    another User has voted it. """
    log.debug("notify_user_join_same_action %s %s" % (sender, kwargs))

    #WAS: if kwargs['created']:
    vote = kwargs['vote_instance']
    post = vote.voted_post
    action = post.action

    if post.is_question():
        voter = vote.user

        extra_context = ({
            "user" : voter,
            "action" : action 
        })
        #recipients
        users = action.referrers

        #print "\nnotification.send users %s\n" % users
        notification.send(users=users, 
            label="user_join_your_action",
            extra_context=extra_context,
            on_site=True, 
            sender=None, 
            now=True
        )

@receiver(post_save, sender=Post)
def notify_user_comment_your_action(sender, **kwargs):
    """ Notify that a user commented an Action to its owners """

    if kwargs['created']:
        post = kwargs['instance']

        if post.is_comment_to_action():
            commenter = post.author
            action = post.action

            extra_context = ({
                "user" : commenter,
                "action" : action
            }) 
            #recipients
            users = post.action.referrers

            notification.send(users=users,
                label="user_comment_your_action",
                extra_context=extra_context,
                on_site=True, 
                sender=None, 
                now=True
            )

#WAS: @receiver(action_get_level_step, sender=Action)
@receiver(post_action_status_update, sender=Action)
def notify_post_status_update(sender, **kwargs):
    """ Notify two events:

    * a joined action reached a level step: this is notified 
    to the voters of the Action;
    * a favourite topic action reached a level step: this is
    notified to the user who are not voters of the Action,
    but are voters of an Action who shares a category with
    the former
    """
 
    #1 joined action reached a level step
    action = sender
    old_status = kwargs['old_status']

    log.debug("Action:%s status:%s" % (action, old_status)) 

    #Matteo switch status values (if READY --> ... else: TODO placeholder)

    if old_status == action_consts.ACTION_STATUS_READY: 

        extra_context = ({
            "action" : action,
            "old_status" : old_status
        }) 
        #recipients
        users = action.voters
        #print "\n\nRecipients: %s" % users

        notification.send(users=users,
            label="joined_action_get_level_step",
            extra_context=extra_context,
            on_site=True, 
            sender=None, 
            now=True
        )

        #2 favourite topic action reached a level step
    else:
        #TODO placeholder old_status other than READY
        pass

@receiver(post_save, sender=ActionRequest)
def register_status_update_activity(sender, **kwargs):
    """ Create a new Activity if the status is 'victory' or 'closed' """
 
    action_request = kwargs['instance']
    action = action_request.action
    user = action_request.sender
    question = action.question
    request_type = action_request.request_type

    # check request type because this is a generic post_save handler

    activity_type_notices_map = {
        ar_consts.REQUEST_TYPE_SET_VICTORY : ae_consts.OA_TYPE_ACTIVITY_SET_VICTORY,
        ar_consts.REQUEST_TYPE_SET_CLOSURE : ae_consts.OA_TYPE_ACTIVITY_SET_CLOSURE, 
    }
    
    if request_type in activity_type_notices_map.keys():

        activity_type = activity_type_notices_map[request_type]

        if kwargs['created']:
            # Send notification to OpenAction staff
            # "status_update_request" --> ask to process it

            log.debug("ACTIVITY with Action:%s activity_type:%s" % (action, activity_type)) 

            activity = Activity(
                user=user,
                content_object=action,
                activity_type=activity_type,
                question=question
            )
            activity.save()

            extra_context = ({
                "action" : action,
            }) 
            #recipients
            users = action.referrers

            notification.send(users=users,
                label="status_update",
                extra_context=extra_context,
                on_site=True, 
                sender=None, 
                now=True
            )

        else:
            # We are updating the action request.
            # If it is processed --> notify sender if it is accepted or not

            if action_request.is_accepted:
                extra_context = ({
                    "action" : action,
                }) 
                #recipients
                users = (sender,)

                notification.send(users=users,
                    label="status_update",
                    extra_context=extra_context,
                    on_site=True, 
                    sender=None, 
                    now=True
                )

#NOTE: KO: the default settings should have been setted in the user pre_save
#@receiver(post_save, sender=User)
#def user_set_default_notice_backend(sender, **kwargs):
#    """ Indicates for the User whether to send notifications
#    of a given type to the openaction default medium. """
#
#    if kwargs['created']:
#        user = kwargs['instance']
#
#        if user.is_active:
#
#            for notice_type in notification.NoticeType.objects.all():
#                obj, created = notification.NoticeSetting.objects.get_or_create(
#                    user=user, 
#                    notice_type=notice_type, 
#                    medium="openaction", 
#                    send=True
#                )
#                log.debug("Adding NoticeSetting of type %s to user %s " % (
#                    notice_type, 
#                    user
#                ))

#handle the moderation requests from the action owner
@receiver(action_moderation_request_submitted, sender=ActionRequest)
def notify_action_moderation_request(sender, **kwargs):
    """ Notify to an action follower that he received a moderation
    request from the action owner"""

    action_request = sender

    #recipients
    if action_request.recipient_set.count() != 0:
        users = action_request.recipient_set.all()
    else:
        # Send notification to staff users
        # OpenPolis/ActionAID people who manage the software
        users = User.objects.filter(is_staff=True)

    #extra_context
    extra_context = ({
        "action_request" : action_request,
        "process_url" : reverse("actionrequest-moderation-process", args=(action_request.pk,))
    }) 

    notification.send(users=users,
        label="mod_proposal",
        extra_context=extra_context,
        on_site=True, 
        sender=None, 
        now=True
    )

@receiver(action_message_sent, sender=ActionRequest)
def notify_action_message_sent(sender, **kwargs):
    """ Notify to action referrers that someone sent a private message
    regarding a referred action.
    """

    action_request = sender

    # Action message is routed to action referrers
    users = action_request.recipient_set.all()

    #extra_context
    extra_context = ({
        "action_request" : action_request,
        "process_url" : reverse("actionrequest-message-reply", args=(action_request.pk,))
    }) 

    notification.send(users=users,
        label="message_your_action",
        extra_context=extra_context,
        on_site=True, 
        sender=None, 
        now=True
    )

@receiver(action_message_replied, sender=ActionRequest)
def notify_action_message_replied(sender, **kwargs):
    """ Notify to the user who sent the private message and to all the 
    action referrers that one of them replied to the message.

    The replier is the referrer who replied to the message.
    """

    action_request = sender
    replier = kwargs['replier']

    users = [action_request.sender]
    #extra_context
    extra_context = ({
        "action_request" : action_request,
        "replier" : replier,
    }) 

    notification.send(users=users,
        label="message_replied_referrers",
        extra_context=extra_context,
        on_site=True, 
        sender=None, 
        now=True
    )

    users = action_request.recipient_set.all()
    #extra_context
    extra_context = ({
        "action_request" : action_request,
        "replier" : replier,
    }) 

    notification.send(users=users,
        label="message_replied_user",
        extra_context=extra_context,
        on_site=True, 
        sender=None, 
        now=True
    )

#handle the moderation processing of the questioned user
@receiver(action_moderation_request_processed, sender=ActionRequest)
def notify_action_moderation_processed(sender, **kwargs):
    """ Notify to the Action owner that an Action follower sent a response
    to an Action moderation request

    """

    action_request = sender

    #recipients
    users = (action_request.action.owner,)

    #extra_context
    extra_context = ({
        "action_request" : action_request,
    }) 

    notification.send(users=users,
        label="answer_mod_proposal",
        extra_context=extra_context,
        on_site=True, 
        sender=None, 
        now=True
    )

@receiver(action_moderator_removed, sender=Action)
def notify_action_moderation_removed(sender, **kwargs):
    """ Notify to an Action moderator that the Action owner removed him
    from the Action moderators list"""

    action = sender
    moderator = kwargs['moderator']

    #recipients
    users = (moderator,)
    #extra_context
    extra_context = ({
        "action" : action,
        "response_url" : reverse("action-message-send", args=(action.pk,))
    }) 

    notification.send(users=users,
        label="mod_removal",
        extra_context=extra_context,
        on_site=True, 
        sender=None, 
        now=True
    )
