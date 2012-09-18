from django.db.models.signals import post_save
from django.dispatch import receiver 

from askbot.models import Post
from notification import models as notification

@receiver(post_save, sender=Post)
def notify_add_blog_post(sender, **kwargs):
    """ Notify to Action referrers and followers that a new post 
    has been added to the Action blog

    #1 set the recipients (the receivers)
    #2 send notification(notification.send)
    
    Possible options:
    * 'now=True and queue=True': error
    * 'now=True and queue=False': send notice immediately by passing 'now=True' to 
    send function
    * 'queue=True and now=False': queue the notice in order to send it later
    * 'now=False and queue=False'(default): let the default notification 
    configuration decide

    QUESTION: should we pass the referrer who created the blog post as the 
    sender of the notice (in sender=)?
    ANSWER: no, the sender is always "the system"
    """

    if kwargs['created']:
        post = kwargs['instance']

        # This is a generic Post post_save handler, 
        # so we have to check if it is an answer
        if post.is_answer():

            action = post.thread.action

            referrers = action.referrers
            followers = action.thread.followed_by.all()
            # recipients
            users = referrers | followers
            
            notification.send(users=users, 
                label="action_make_notice", 
                extra_context=None, 
                on_site=True, 
                sender=None, 
                now=True
            )
 
