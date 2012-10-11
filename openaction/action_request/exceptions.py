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

class RecipientRequestActionMessageNotReferrersException(exceptions.PermissionDenied):

    def __init__(self, user, action):
        self.user = user
        self.action = action

    def __unicode__(self):
        return u"L'utente %s può inviare un messaggio privato esclusivamente ai referenti dell'azione %s" % (self.user, self.action)

class CannotSendMessageToReferrers(exceptions.PermissionDenied):

    def __init__(self, action_request):
        self.sender = action_request.sender
        self.action = action_request.action

    def __unicode__(self):
        return u"L'utente %s non può inviare un  messagio ai referenti dell'azione %s perchè ha già inviato loro %s messaggi." % (self.sender, settings.MAX_DELIVERABLE_MESSAGES, self.action)

class UserCannotReplyToPrivateMessage(exceptions.PermissionDenied):

    def __init__(self, action_request):
        self.sender = action_request.sender
        self.recipients = action_request.recipient_set.all()
        self.action = action_request.action

    def __unicode__(self):
        return u"L'utente %s non è un referente per l'azione %s e quindi non può rispondere al messaggio privato inviatogli dall'utente %s." % (self.recipients[0], self.action, self.sender)

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

class UserCannotProcessARequestTwice(exceptions.PermissionDenied):

    def __init__(self, action):
        self.action = action

    def __unicode__(self):
        return u"La richiesta di moderazione per l'azione %s risulta essere già stata processata" % (self.action)
