from django.db import models
from askbot.models import User
from django.utils.translation import ugettext as _
from django.conf import settings

from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from django.dispatch import receiver 

from notification import models as notification
from oa_notification import consts


#--------------------------------------------------------------------------------

def create_notice_types(app, created_models, verbosity, **kwargs):
    """Define notice types and default 'spam_sensitivity'.

    `spam_sensitivity` states default for sending message through a `backend`.
    If `spam_sensitivity` if > than `backend.spam_sensitivity`, then message is
    not sent through that medium.

    `EmailBackend.spam_sensitivity` = 2

    This in turn is saved as a default `NoticeSetting` that could be (eventually)
    changed by User in notification preferences panel.
    """

    # Mail notifications: category A
    notification.create_notice_type(
        consts.ACTION_MAKE_BLOGPOST, "Creata una nuova notizia",
        "una azione ha prodotto una nuova notizia", default=2
    )

    notification.create_notice_type(
        "friend_join_same_action", _("Action Joined"),
        _("a friend joined the same action you also have joined"), default=2
    )

    notification.create_notice_type(
        "friend_create_action", _("Action Created"),
        _("a friend created a new action"), default=2,
    )

    notification.create_notice_type(
        "new_local_action", _("Action Created"),
        _("a new local action was created"), default=2
    )

    notification.create_notice_type(
        "user_comment_your_action", _("Action Commented"),
        _("someone commented a blog post of your action"), default=2
    )

    notification.create_notice_type(
        "mod_proposal", _("Moderator Proposal"),
        _("an action owner offered you to become a moderator"), default=2
    )
    ##### added by Matteo
    notification.create_notice_type(
        "mod_removal", _("Moderator removal"),
        _("the action owner removed you from the action moderators"), default=2
    )
    notification.create_notice_type(
        "status_update", _("Action status update request"),
        _("an action owner would like to change its action status"), default=2
    )
    notification.create_notice_type(
        "message_replied_user", _("Message reply to user"),
        _("an action referrer replied to a message you sent"), default=2
    )
    notification.create_notice_type(
        "message_replied_referrers", _("Referrer replied to message"),
        _("an action referrer replied to a message sent by a user to the action you are referring"), default=2
    )
    ######
    notification.create_notice_type(
        "answer_mod_proposal", _("Answer Received"),
        _("you received an answer about your moderator proposal"), default=2,
    )

    notification.create_notice_type(
        "message_your_action", _("Message Received"),
        _("an user sent you a message about your action"), default=2
    )

    # notification: category B
    notification.create_notice_type(
        "user_join_your_action", _("Action Joined"),
        _("a user joined your action"), default=2
    )

    notification.create_notice_type(
        "user_comment_same_action", _("Blog Commented"),
        _("a user commented a blog post of an action you also have joined"), default=2
    )

    notification.create_notice_type(
        "new_fav_topic_action", _("Action Created"),
        _("a topic with favourite topic has just created"), default=2,
    )

    notification.create_notice_type(
        "politician_answer", _("Politician Answered"),
        _("a politician expressed an opinion about an action"), default=2
    )

    notification.create_notice_type(
        "friend_join_action", _("Action Joined"),
        _("a friend joined in an action"), default=2
    )

    notification.create_notice_type(
        "friend_comment_action", _("Blog Commented"),
        _("a friend commented the blog of an action"), default=2
    )

    notification.create_notice_type(
        "joined_action_get_level_step", _("Level Step Reached"),
        _("a joined action reached a level step"), default=2,
    )

    notification.create_notice_type(
        "fav_topic_action_get_level_step", _("Level Step Reached"),
        _("a favourite topic action reached a level step"), default=2
    )

    notification.create_notice_type(
        "friend_follow_association", _("Association Followed"),
        _("your friend began following an association"), default=2
    )

    notification.create_notice_type(
        "association_publish_something", _("Publication Created"),
        _("an association you're following published something"), default=2
    )

#--------------------------------------------------------------------------------

def set_default_notice_settings(user):

    # Add openaction backend for sending notices to the user.
    # when a User is activated
    # Note: we need to get the index of the backands list because 
    # 'notification' needs the index, not the name
    medium = settings.NOTIFICATION_BACKENDS.index(("openaction", "oa_notification.backends.openaction.OpenActionDefaultBackend"))
    for notice_type in notification.NoticeType.objects.all():
        notification.get_notification_setting(user=user,
            notice_type=notice_type,
            medium=medium
        )

@receiver(post_save, sender=User)
def post_user_set_default_notice_settings(sender, **kwargs):
    """ Create a NoticeSetting instance for the User, using default (openaction) 
    backend
    
    Case: user is being created and user is active
    """
    if kwargs['created']:
        user = kwargs['instance']
        if user.is_active:
            set_default_notice_settings(user)

@receiver(pre_save, sender=User)
def pre_user_set_default_notice_settings(sender, **kwargs):
    """ Create a NoticeSetting instance for the User, using default (openaction) 
    backend

    Case: user is being modified as active and user was not active before the modification
    """

    user = kwargs['instance']

    if user.pk and user.is_active:

        try:
            old_user = User.objects.get(pk=user.pk)
        except User.DoesNotExist as e:
            return

        if not old_user.is_active:
            set_default_notice_settings(user)

