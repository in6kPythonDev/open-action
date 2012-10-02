
from askbot.const import *
from django.utils.translation import ugettext as _

OA_TYPE_ACTIVITY_SET_VICTORY = 100
OA_TYPE_ACTIVITY_SET_CLOSURE = 101

TYPE_ACTIVITY_CHOICES = (

    (OA_TYPE_ACTIVITY_SET_VICTORY, "impostato la vittoria sull'azione"),
    (OA_TYPE_ACTIVITY_SET_CLOSURE, "impostato la chiusura sull'azione"),

    # TODO: Matteo or Antonio: rinominare la descrizione
    (TYPE_ACTIVITY_ASK_QUESTION, _('asked a question')),
    (TYPE_ACTIVITY_ANSWER, _('answered a question')),
    (TYPE_ACTIVITY_COMMENT_QUESTION, _('commented question')),
    (TYPE_ACTIVITY_COMMENT_ANSWER, _('commented answer')),
    (TYPE_ACTIVITY_UPDATE_QUESTION, _('edited question')),
    (TYPE_ACTIVITY_UPDATE_ANSWER, _('edited answer')),
    (TYPE_ACTIVITY_PRIZE, _('received badge')),
    (TYPE_ACTIVITY_MARK_ANSWER, _('marked best answer')),
    (TYPE_ACTIVITY_VOTE_UP, _('upvoted')),
    (TYPE_ACTIVITY_VOTE_DOWN, _('downvoted')),
    (TYPE_ACTIVITY_CANCEL_VOTE, _('canceled vote')),
    (TYPE_ACTIVITY_DELETE_QUESTION, _('deleted question')),
    (TYPE_ACTIVITY_DELETE_ANSWER, _('deleted answer')),
    (TYPE_ACTIVITY_MARK_OFFENSIVE, _('marked offensive')),
    (TYPE_ACTIVITY_UPDATE_TAGS, _('updated tags')),
    (TYPE_ACTIVITY_FAVORITE, _('selected favorite')),
    (TYPE_ACTIVITY_USER_FULL_UPDATED, _('completed user profile')),
    (TYPE_ACTIVITY_EMAIL_UPDATE_SENT, _('email update sent to user')),
    (
        TYPE_ACTIVITY_UNANSWERED_REMINDER_SENT,
        _('reminder about unanswered questions sent'),
    ),
    (
        TYPE_ACTIVITY_ACCEPT_ANSWER_REMINDER_SENT,
        _('reminder about accepting the best answer sent'),
    ),
    (TYPE_ACTIVITY_MENTION, _('mentioned in the post')),
    (
        TYPE_ACTIVITY_CREATE_TAG_WIKI,
        _('created tag description'),
    ),
    (
        TYPE_ACTIVITY_UPDATE_TAG_WIKI,
        _('updated tag description')
    ),
    (TYPE_ACTIVITY_MODERATED_NEW_POST, _('made a new post')),
    (
        TYPE_ACTIVITY_MODERATED_POST_EDIT,
        _('made an edit')
    ),
    (
        TYPE_ACTIVITY_CREATE_REJECT_REASON,
        _('created post reject reason'),
    ),
    (
        TYPE_ACTIVITY_UPDATE_REJECT_REASON,
        _('updated post reject reason')
    ),
    (
        TYPE_ACTIVITY_VALIDATION_EMAIL_SENT,
        'sent email address validation message'#don't translate, internal
    ),

)
