# -*- coding: utf-8 -*-

class ActionInvalidStatusException(Exception):
    pass

class InvalidReferralError(Exception):
    
    def __unicode__(self):
        #TODO Matteo: italian
        return u"A User cannot be referred by himself"

class UserCannotVoteTwice(Exception):
    
    def __init__(self, user, action):
        self.user = user
        self.action = action  

    def __str__(self):
        #TODO Matteo: unicode italian
        return "The user %s has already voted the Action %s" % (self.user,
            self.action)
        
