from django.template.loader import render_to_string
from django.template import Context
from django.utils.translation import ugettext

from notification.backends.base import BaseBackend
#WAS: from notification.models import Notice

class OpenActionDefaultBackend(BaseBackend):

    spam_sensitivity = 2

    def deliver(self, recipient, sender, notice_type, extra_context):
        """ Deliver a notice to a User 

        DefaultBackend.deliver will send to the receiver (a User) a 
        notification of an action triggered by some other User on an 
        Action or on some article related to it
        """  

        # Inspired from django-notification-brosner.backends.EmailBackend
        # 1. Get formatted messages
        context = Context({
            "recipient": recipient,
            "sender": sender,
            "notice": ugettext(notice_type.display),
        })
        context.update(extra_context)

        messages = self.get_formatted_messages((
            "short.txt",
            "full.txt"
        ), notice_type.label, context)

        # 2. Render them with on-site site-wide notification templates
        subject = render_to_string("notification/on_site_notice_subject.txt", {
            "message": messages["short.txt"],
        }, context)
        
        text = render_to_string("notification/on_site_notice_text.txt", {
            "message": messages["full.txt"],
        }, context)

        notice_text = u"%s%s" % (subject, text)

        # 3. Deliver notice = save new notice for User 'recipient'
        from notification.models import Notice
        Notice.objects.create(recipient=recipient, 
            message=notice_text,
            notice_type=notice_type,
            on_site=True
        )
        
