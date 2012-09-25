# -*- coding: utf-8 -*-

from django.core import exceptions

class UserCannotFollowOrgTwice(exceptions.PermissionDenied):

    def __init__(self, user, org):
        self.user = user
        self.org = org

    def __unicode__(self):
        return u"L'utente %s sta già seguendo l'associazione %s" % (self.user, 
        self.org)

class UserCannotRepresentOrgTwice(exceptions.PermissionDenied):

    def __init__(self, user, org):
        self.user = user
        self.org = org

    def __unicode__(self):
        return u"L'utente %s rappresenta già l'associazione %s" % (self.user, 
        self.org)
