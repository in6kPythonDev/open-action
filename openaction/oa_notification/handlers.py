from django.db.models.signals import post_save
from django.dispatch import receiver 

from askbot.models import Post, User
from askbot.models.repute import Vote
from notification import models as notification
from action.models import Action
from action.signals import post_action_status_update 

from oa_notification import consts

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
                label=consts.ACTION_MAKE_BLOGPOST, 
                extra_context=extra_context, 
                on_site=True, 
                sender=None, 
                now=True
            )

#TODO: Matteo dedicated signal: post_declared_vote_add
@receiver(post_save, sender=Vote)
def notify_user_join_same_action(sender, **kwargs): #TODO Matteo your action
    """ Notify to the users who woted an Action that 
    another User has voted it. """
    print "notify_user_join_same_action %s %s" % (sender, kwargs)

    if kwargs['created']:
        vote = kwargs['instance']
        post = vote.voted_post
        action = post.thread.action

        if post.is_question():
            voter = vote.user

            extra_context = ({
                "user" : voter,
                "action" : action 
            })
            #recipients
            #for user in action.voters:
            #    print "user: %s" % User.objects.get(username=user.get('user__username'))
            users = []
            for user in action.voters:
                users.append(User.objects.get(username=user.get('user__username')))
        
            print "\nnotification.send users %s\n" % users
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
            action = post.thread.action #TODO Matteo: post.action

            extra_content = ({
                "user" : commenter,
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
@receiver(post_action_status_update, sender=Action)
#TODO Matteo: rename post_status_update
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
    status = kwargs['old_status']

    print "\n\n------action:%s status:%s\n\n" % (action,status) 

    #TODO: Matteo switch status values (if READY --> ... else: TODO placeholder)

    extra_context = ({
        "action" : action,
        "old_status" : status
    }) 
    #recipients
    users = action.voters
    print "\n\nRecipients: %s" % users

    notification.send(users=users,
        label="joined_action_get_level_step",
        extra_context=extra_context,
        on_site=True, 
        sender=None, 
        now=True
    )

    #2 favourite topic action reached a level step

@receiver(post_save, sender=User)
def notify_user_comment_your_action(sender, **kwargs):
    """ Indicates for the User whether to send notifications
    of a given type to the openaction default medium. """

    if kwargs['created']:
        user = kwargs['instance']

        if user.is_active:

            for notice_type in notification.NoticeType.objects.all():
                obj, created = notification.NoticeSetting.objects.get_or_create(
                    user=user, 
                    notice_type=notice_type, 
                    medium="openaction", 
                    send=True
                )
                print "Adding NoticeSetting of type %s to user %s " % (notice_type, 
                    user
                ) 
