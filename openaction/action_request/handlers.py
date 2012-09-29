#from django.dispatch import receiver
#from django.conf import settings
#from django.urls.urlresolvers import reverse
#
#from action_request.signals import action_moderation_request_submitted
#from action_request.models import ActionRequest
#from notification import models as notification
#
#import logging
#
#log = logging.getLogger(settings.PROJECT_NAME)
#
##handle the moderation requests from the action owner
#
#@receiver(action_moderation_request_submitted, sender=ActionRequest):
#def notify_action_moderation_request(sender, **kwargs):
#    """ Notify to an action follower that he received a moderation
#    request from the action owner"""
#
#    action_request = sender
#
#    #recipients
#    users = action_request.recipient
#    #extra_context
#    extra_context = ({
#        "action_request" : action_request
#        "process_url" : reverse("actionrequest-moderation-process", args=(action_request.pk,))
#    }) 
#
#    notification.send(users=users,
#        label="",
#        extra_context=extra_context,
#        on_site=True, 
#        sender=None, 
#        now=True
#    )
