from notification.backends.base import BaseBackend

class DefaultBackend(BaseBackend):

    def deliver(self, recipient, sender, notice_type, extra_content):
        """ Deliver a notice to a User 

        DefaultBackend.deliver will send to the receiver (a User) a 
        notification of an action triggered by some other User on an 
        Action or on some article related to it
        """  

        oa_recipient = recipient
        
        #create notice for User 'oa_recipient' of type 'notice_type'
        notice = UserNotice(oa_recipient, notice_type)
        notice.save()

        return super(DefaultBackend, self).deliver(
            oa_recipient, sender, notice_type, extra_content
        )
        
