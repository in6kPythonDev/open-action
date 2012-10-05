# -*- coding: utf-8 -*-

from django.core import exceptions
from django.conf import settings

class RequestActionModerationNotOwnerException(exceptions.PermissionDenied):

    def __init__(self, user, action):
        self.user = user
        self.action = action

    def __unicode__(self):
        return u"L'utente %s non può richiedere la moderazione dell'azione %s poichè non ne è l'autore" % (self.user, self.action)

class CannotRequestModerationToUser(exceptions.PermissionDenied):

    def __init__(self, user, follower, action):
        self.user = user
        self.follower = follower
        self.action = action

    def __unicode__(self):
        return u"L'utente %s non può richiedere la moderazione dell'azione %s all'utente %s per più di %s volte." % (self.user,
            self.action, 
            self.follower,
            settings.MAX_MODERATION_REQUESTS
        )

class UserCannotModerateActionException(exceptions.PermissionDenied):

    def __init__(self, user, action):
        self.user = user
        self.action = action

    def __unicode__(self):
        return u"L'utente %s non puo moderare l'azione %s poichè non la sta seguendo" % (self.user, self.action)

class UserCannotUpdateAlreadyAcceptedModerationRequest(exceptions.PermissionDenied):

    def __init__(self, user, action):
        self.user = user
        self.action = action

    def __unicode__(self):
        return u"L'utente %s ha già accettato di moderare l'azione %s" % (self.user, self.action)

class SenderRequestActionMessageNotReferrerException(exceptions.PermissionDenied):

    def __init__(self, user, action):
        self.user = user
        self.action = action

    def __unicode__(self):
        return u"L'utente %s non può inviare un messaggio privato perchè non riferisce l'azione %s" % (self.user, self.action)

class RecipientRequestActionMessageNotReferrerException(exceptions.PermissionDenied):

    def __init__(self, user, recipient, action):
        self.user = user
        self.recipient = recipient,
        self.action = action

    def __unicode__(self):
        return u"L'utente %s che riferisce l'azione %s non può inviare un messaggio privato all'utente %s perchè questo non riferisce l'azione" % (self.user, self.action, self.recipient)

class UserCannotReplyToReferrerMessage(exceptions.PermissionDenied):

    def __init__(self, action_request):
        self.sender = action_request.sender
        self.recipient = action_request.recipient
        self.action = action_request.action

    def __unicode__(self):
        return u"L'utente %s non può rispondere al messagio inviatogli dal referente %s dell'azione %s perchè non è a sua volta un referente per l'azione" % (self.recipient, self.sender, self.action)

class UserCannotAskActionUpdate(exceptions.PermissionDenied):
    #TODO: think about a more detailed exception error message, taking in account the status the user want to update the action to

    def __init__(self, user, action):
        self.user = user
        self.action = action

    def __unicode__(self):
        return u"L'utente %s non può richiedere un cambio di stato dell'azione %s perchè non la riferisce" % (self.user, self.action)

class ActionStatusUpdateRequestAlreadySent(exceptions.PermissionDenied):

    def __init__(self, user, action):
        self.user = user
        self.action = action

    def __unicode__(self):
        return u"L'utente %s ha già richiesto un cambio di stato dell'azione %s per cui non ha ancora ricevuto riposta." % (self.user, self.action)
