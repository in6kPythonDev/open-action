from notification.backends.base import BaseBackend

from oa_notification.models import UserNotice

class OpenActionDefaultBackend(BaseBackend):

    def deliver(self, recipient, sender, notice_type, extra_content):
        """ Deliver a notice to a User 

        DefaultBackend.deliver will send to the receiver (a User) a 
        notification of an action triggered by some other User on an 
        Action or on some article related to it
        """  

        # Inspired from django-notification-brosner.backends.EmailBackend
        # 1. Get formatted messages
        # TODO: Matteo
        # 2. Render them with on-site site-wide notification templates
        # TODO: Matteo
        # 3. Deliver notice = save new notice for User 'recipient'

        UserNotice.objects.create(user=recipient, text=notice_text)
        
