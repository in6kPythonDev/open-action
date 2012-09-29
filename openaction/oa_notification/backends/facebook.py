from notification.backends.email import EmailBackend

class FBInboxBackend(EmailBackend):

    def deliver(self, recipient, sender, notice_type, extra_content):
        """Deliver to facebook happens overriding User email attribute.

        EmailBackend.deliver will send notice to recipient.email"""

        fb_recipient = recipient

        try:
            fb_recipient.email = recipient.get_external_info('facebook')['email']
        except KeyError as e:
            raise ValueError("User %s recipient, has no facebook info 'email'" % fb_recipient)

        return super(EmailBackend, self).deliver(
            fb_recipient, sender, notice_type, extra_content
        )
