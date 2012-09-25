from django.db import models

from action.models import Action
from askbot.models.user import User



class ActionRequest(models.Model, Resource):
    """ A request,from moderators to the staff,to make operations on an Action
    
    An ActionRequest is raised from an Action moderator whether he wants 
    to make some operation on it, only if the operation requires the staff 
    permissions 
    """

    REQUEST_CHOICES = (
        ('moderation','Moderazione'),
        ('message','Messaggio'),
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
