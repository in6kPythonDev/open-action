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
        return u"L'utente %s non puo moderare l'azione % poichè non la sta seguendo" % (self.user, self.action)
