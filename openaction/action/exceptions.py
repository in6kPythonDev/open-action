# -*- coding: utf-8 -*-

from action import const as action_const

class ActionInvalidStatusException(Exception):
    
    def __init__(self, status):
        if status == action_const.ACTION_STATUS_DRAFT:
            self._status = "in stato bozza"
        elif status == action_const.ACTION_STATUS['deleted']:
            self._status = "stata cancellata"
        elif status == action_const.ACTION_STATUS['closed']:
            self._status = "stata chiusa"
         

class VoteActionInvalidStatusException(ActionInvalidStatusException):
    
    def __unicode__(self):
        return u"L'azione non può essere votata perchè è %s." % self._status

class CommentActionInvalidStatusException(ActionInvalidStatusException):
    
    def __unicode__(self):
        return u"L'azione non può essere commentata perchè è %s." % self._status

class BlogpostActionInvalidStatusException(ActionInvalidStatusException):
    
    def __unicode__(self):
        return u"Non è possibile aggiungere un articol al blog dell'azione perchè questa è %s." % self._status

class InvalidReferralError(Exception):
    
    def __unicode__(self):
        return u"Un utente non può avere se stesso come referente del voto."

class UserCannotVoteTwice(Exception):
   
    def __init__(self, user, post):
        self.user = user
        if post.post_type == 'question':
            self._post_type = "questa azione"
        elif post.post_type == 'answer':
            self._post_type = "questa risposta"
        elif post.post_type == 'comment':
            self._post_type = "questo commento"

    def __unicode__(self):
        return u"L'utente %s ha già votato %s." % (self.user,
            self._post_type)
        
class UserCannotVote(UserCannotVoteTwice):

    def __unicode__(self):
        return u"L'utente %s non può votare %s." % (self.user,
            self._post_type)
        
