from django.db import models

from base.models import Resource
from action.models import Action
from askbot.models.user import User
from action_request import const


class ActionRequest(models.Model, Resource):
    """ A registry of requests related to actions.

    Each request has fields to be processed and to be answered
    if it is a boolead (is_accepted) or freetext answer (answer_notes). 
    When a freetext answer is processed is_accepted is set to True.

    Here is a list of requests that can be issued:

    * moderator reguest: issued by the owner of the action to a follower
    * message request: issued by a user to referrers of the action
    * set_victory request: issued by a referrer of the action to OpenAction staff (NULL recipient)
    """

    #TODOFUTURE: this could be implemented with GenericForeignKey
    # to decouple it from action. Another solution could be to use
    # 3 fields: action, organization, politician to support binding to other
    # resources. Evaluate use cases.
    # If decoupled it could be used also for:
    # * org representation request: issued to a user to represent an organization
    # * add politician mail request to suggest a new for a politician

    #TODOFUTURE: Every action that use this application should be able to define its
    # REQUEST_TYPE_CHOICES
    REQUEST_CHOICES = (
        (const.REQUEST_TYPE['mod'],'Moderazione'),
        (const.REQUEST_TYPE['msg'],'Messaggio'),
    ) 
    
    action = models.ForeignKey(Action)
    sender = models.ForeignKey(User, null=True, blank=True, related_name="request_set")
    recipient = models.ForeignKey(User, null=True, blank=True, related_name="request_receiver_set")
    request_type = models.CharField(max_length=256, choices=REQUEST_CHOICES)
    request_notes = models.TextField(blank=True, default="")
    answer_notes = models.TextField(blank=True, default="")
    is_accepted = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)
    last_update_on = models.DateTimeField(auto_now=True)
        
    def check_same_type_already_accepted(self):
        return ActionRequest.objects.filter(
            recipient=self.recipient, action=self.action,
            request_type=self.request_type, is_accepted=True
        ).exists()

    def check_same_type_already_processed(self):
        return ActionRequest.objects.filter(
            recipient=self.recipient, action=self.action,
            request_type=self.request_type, is_processed=True
        ).exists()


