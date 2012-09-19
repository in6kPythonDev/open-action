from django.db.models.signals import post_save
from django.dispatch import receiver 

from askbot.models import Post
from askbot.models.repute import Vote
from notification import models as notification
from action.models import Action
from action.signals import action_get_level_step

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

            extra_context = ({
                "blog_post" : post,
                "action" : action
            })

            notification.send(users=users, 
                label="action_make_notice", 
                extra_context=extra_context, 
                on_site=True, 
                sender=None, 
                now=True
            )

@receiver(post_save, sender=Vote)
def notify_user_join_same_action(sender, **kwargs):
    """ Notify to the users who woted an Action that 
    another User has voted it. """

    if kwargs['created']:
        vote = kwargs['instance']
        post = vote.voted_post

        if post.is_question():
            voter = vote.user

            extra_content = ({
                "user" : voter
                "action" : action,
            })
            #recipients
            users = action.voters
            
            notification.send(users=users, 
                label="user_join_same_action", 
                extra_context=extra_context, 
                on_site=True, 
                sender=None, 
                now=True
            )

@receiver(post_save, sender=Post)
def notify_user_comment_your_action(sender, **kwargs):
    """ Notify that a user commented an Action to its owners """

    if kwargs['created']:
        post = kwargs['instance']

        if post.is_comment_to_action():
            commenter = post.author
            action = post.thread.action

            extra_content = ({
                "user" : commenter
                "action" : action
            }) 
            #recipients
            users = post.thread.action.referrers

            notification.send(users=users,
                label="user_comment_your_action",
                extra_context=extra_context,
                on_site=True, 
                sender=None, 
                now=True
            )

#@receiver(action_get_level_step, sender=Action)
@receiver(action_get_level_step)
def notify_action_get_level_step(sender, **kwargs):
    """ Notify two events:

    * a joined action reached a level step: this is notified 
    to the voters of the Action;
    * a favourite topic action reached a level step: this is
    notified to the user who are not voters of the Action,
    but are voters of an Action who shares a category with
    the former
    """
 
    #1 joined action reached a level step
    action = sender
    status = kwargs['status']

    print "\n\n------action:%s status:%s\n\n" % (action,status) 

    extra_content = ({
        "action" : action,
        "status" : status
    }) 
    #recipients
    users = action.voters

    notification.send(users=users,
        label="joined_action_get_level_step",
        extra_context=extra_context,
        on_site=True, 
        sender=None, 
        now=True
    )

    #2 favourite topic action reached a level step
