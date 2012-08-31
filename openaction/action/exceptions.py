# -*- coding: utf-8 -*-

class ActionInvalidStatusException(Exception):
    pass

class InvalidReferralError(Exception):
    
    def __unicode__(self):
        #QUESTION: exception should be in first person or in third person?
        return u"Un utente non può avere se stesso come referente del voto."

class UserCannotVoteTwice(Exception):
    
    def __init__(self, user, action):
        self.user = user
        self.post = post

    def __unicode__(self):
        #QUESTION: exception should be in first person or in third person?
        return "L'utente ha già votato questo post." % (self.user,
            self.action)
        
