from django.db import models
from notification import models as notification


#------------------------------------------------------------------------------

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
        "action_make_notice", _("Notice Created"),
        _("an action produced a notice"), default=2
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

    notification.create_notice_type(
        "answer_mod_proposal", _("Answer Received"),
        _("you received an answer about your moderator proposal"), default=2,
    )

    notification.create_notice_type(
        "message_your_action", _("Message Received"),
        _("an user sent you a message about your action"), default=2
    )

    # Mail notification: category B
    notification.create_notice_type(
        "user_join_same_action", _("Action Joined"),
        _("a user joined the same action you also have joined"), default=2
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
        "local_politician_answer", _("Politician Answered"),
        _("a local politician answered about an action"), default=2
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
        "local_action_get_level_step", _("Level Step Reached"),
        _("a local action reached a level step"), default=2,
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
        "association_public_something", _("Publication Created"),
        _("an association you're following published something"), default=2
    )
