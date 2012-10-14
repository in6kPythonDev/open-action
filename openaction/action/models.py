# -*- coding: utf-8 -*-

from django.db import models, transaction
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from askbot.models import Thread, User
from askbot.models.post import Post
from askbot.models.repute  import Vote

from base.models import Resource
from base.utils import get_resource_icon_path

from action import const, exceptions, tokens, managers
from action.signals import post_action_status_update
from organization.models import Organization
from external_resource.models import ExternalResource

import askbot_extensions.utils
import logging, datetime, os

from django.conf import settings

log = logging.getLogger(settings.PROJECT_NAME)


#--------------------------------------------------------------------------------

def get_action_image_path(instance, filename):

    ext = filename.split('.')[-1]
    base_path = "action_images"
    return os.path.join(base_path, str(instance.pk), slugify(instance.bare_title), ext)

class Action(models.Model, Resource):

    # Extending Askbot model!
    thread = models.OneToOneField(Thread)

    victory = models.BooleanField(default=False)
    _threshold = models.PositiveIntegerField(blank=True, null=True)

    created_by = models.ForeignKey(User, related_name="created_action_set")
    in_nomine_org = models.ForeignKey(Organization, null=True, blank=True,
        help_text="azione aperta per conto dell'associazione..."
    )

    moderator_set = models.ManyToManyField(User, null=True, blank=True, related_name="moderated_action_set")
    geoname_set = models.ManyToManyField('Geoname', null=True, blank=True)
    category_set = models.ManyToManyField('ActionCategory', 
        null=True, blank=True,
        help_text=u"La scelta degli argomenti può aiutarti a definire meglio i prossimi passi"
    )
    politician_set = models.ManyToManyField('Politician', null=True, blank=True)
    media_set = models.ManyToManyField('Media', null=True, blank=True)

    image = models.ImageField(null=True, blank=True, upload_to=get_action_image_path)

    objects = managers.ActionManager()

    class Meta:
        get_latest_by = "thread"
        ordering = ['-thread']

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("action-detail", args=(self.pk,))
    

    # Status can be 
    # DRAFT, READY, CANCELED, ACTIVE, CLOSED, VICTORY
    @property
    def status(self):

        if self.victory:
            status = const.ACTION_STATUS_VICTORY
        elif self.thread.closed:
            status = const.ACTION_STATUS_CLOSED
        elif self.question.deleted:
            status = const.ACTION_STATUS_DELETED
        #was: elif self.score == 0:
        elif not self._threshold:
            # cannot be voted until all fields are set
            # so the Action goes into "ready" status
            status = const.ACTION_STATUS_DRAFT
        elif self.score < self.threshold:
            status = const.ACTION_STATUS_READY
        elif self.score >= self.threshold:
            status = const.ACTION_STATUS_ACTIVE

        return status

    def status_display(self):
        return const.ACTION_STATUS[self.status]

    def update_status(self, value):
        """ Update status and save it """

        old_status = self.status
        if value == const.ACTION_STATUS_VICTORY:
            self.victory = True
            self.save()
        elif value == const.ACTION_STATUS_CLOSED:
            self.thread.closed = True
            self.thread.save()
        elif value == const.ACTION_STATUS_DELETED:
            self.question.deleted = True
            self.question.save()
        elif value == const.ACTION_STATUS_DRAFT:
            log.warning("Setting of DRAFT status, this shouldn't be done")
            self.question.score = 0
            self._threshold = None
            self.question.save()
            self.save()
        elif value == const.ACTION_STATUS_READY:
            log.warning("Setting of READY status, this should be done only by bot")
            assert self.threshold #Force threshold computation
        else:
            raise ValueError("Invalid status %s for action %s" % (value, self))

        post_action_status_update.send(sender=self,
            old_status=old_status
        )

    @property
    def question(self):
        """ Question holds the main content for an Action.

        It is an askbot Post of type ``question``
        """
        #DONE: thread extension (see `askbot_extensions.models` app)
        return self.thread.question
        

    @property
    def owner(self):
        """ The owner is the User who posted this action question. """

        #WAS: post = self.thread.posts.get(post_type='question')
        #WAS: return post.author
        return self.question.author
    
    @property
    def referrers(self):
        """ The owner of the Action togheter with the Action moderators """

        owners = User.objects.filter(pk=self.owner.pk)
        moderators = self.moderator_set.all()

        return owners | moderators

    @property
    def followers(self):
        """ The users who are following the Action """

        return self.thread.followed_by.all()

    @property
    def pingbacks(self):
        pass

    @property
    def created_on(self):
        return self.question.added_at
    
    @property
    def geonames(self):
        return self.geoname_set.all()

    @property
    def categories(self):
        return self.category_set.all()

    @property
    def politicians(self):
        return self.politician_set.all()

    @property
    def medias(self):
        return self.media_set.all()

    @property
    def activists(self):
        pass
    
    @property
    def relateds_by_owner(self):
        ''' Actions which have the same authors
        '''
        return Action.objects.filter(thread__question__author=self.owner)

    @property
    def title(self):
        status = ""
        if self.status != const.ACTION_STATUS_ACTIVE:
            status = u" [%s]" % self.status_display()
        return u"%s%s" % (self.bare_title, status)

    @property
    def bare_title(self):
        return self.thread.title

    def update_title(self, value):
        self.thread.title = value
        self.thread.save()
    
    # AGREED: no need for description in this version of OpenAction
#    @property
#    def description(self):
#        """Description is a quite short summary of the action"""
#
#        # TODO TOTHINK 
#        # Askbot summary is 300 chars long, we should enlarge it...
#        return self.question.summary
#
#    def update_description(self, value):
#        self.question.summary = value
#        self.question.save()
    
    @property
    def score(self):
        return self.question.score

    @property
    def content(self):
        return self.question.text

    def update_content(self, value):
        self.question.text = value
        self.question.save()

    @property
    def votes(self):
        #NOTE: self.question.votes returns a RelatedManager on which the methods
        # 'declareds' and 'anonymous' of VoteManager cannot be called
        #WAS: return Vote.objects.all() & self.question.votes.all()
        return Vote.objects.filter(voted_post=self.question)

    @property
    def voters(self):
        """Return User queryset containing users who declared their votes for this action."""
        declared_votes = self.votes.declareds()
        users_pk = declared_votes.values_list('user__pk', flat=True).order_by('-voted_at') 
        return User.objects.filter(pk__in=users_pk)

    @property
    def comments(self):
        '''Return a post queryset of type "comments".
        
        From each comment we find:
        * author --> comment.author
        * author.place --> comment.author.place TODO
        * creation datetime --> comment.added_at, 
        * text --> comment.text, 
        * score --> comment.score
        '''
        return self.question.comments.all()
    
    @property
    def blog_posts(self):
        ''' 
        The blog posts are answers to an Askbot question
        
        How to find the creation datetime, 
        the author, 
        the comments related to the posts,
        an 'is_automatic'-like field in the Post model in order to
        create a new Post once a Question reach its threshold 
        '''
        return self.thread.posts.filter(post_type="answer")

    def compute_threshold(self):
        #TODO: Matteo
        """Compute threshold for an action to become ACTIVE.

        Threshold is the number of votes needed for an action to be
        published and activate media and politicians contacts.
        """

        if self.can_be_ready(): #TODO Matteo: se ce stanno tutti i parametri
            #TODO
            threshold = 3
        else:
            raise exceptions.ThresholdNotComputableException(self)
        return threshold

    @property
    def threshold(self):
        """Return threshold to make the action ACTIVE.

        Compute it if not already computed.
        """

        if not self._threshold:
            self._threshold = self.compute_threshold()
            self.save()
        return self._threshold

    def can_be_ready(self):
        """ Check if it is possible to compute the threshold for an
        Action """
        return self.bare_title != '' and self.content != ''

    token_generator = tokens.ActionReferralTokenGenerator()
    def get_token_for_user(self, user):
        """Return token for user to share that action.

        In this way the user can be recognized as referral for a vote,
        or just (maybe in future) for viewing the action page.

        Token is generated on couple (action, user)
        """
        
        return self.token_generator.make_token((self, user)) 
        #KO: return self.token_generator._make_token_with_timestamp(
        #KO:     (self, user), 
        #KO:     int(datetime.datetime.now().strftime("%s"))
        #KO: ) 

    def get_user_from_token(self, token):
        """Return User instance corresponding to token.

        If invalid raise InvalidReferralTokenException.
        """
        try:
            # get the User instance
            user_pk = self.token_generator.get_user_pk_from_token(token)
            user_calling_for_action = User.objects.get(pk=user_pk)
        except Exception as e:
            raise exceptions.InvalidReferralTokenException()

        checked = self.token_generator.check_token((self, user_calling_for_action), token)

        log.debug("Token checked=%s for action=%s, user=%s" % (checked, self, user_calling_for_action))

        if checked:
            #return user
            return user_calling_for_action
        else:
            raise exceptions.InvalidReferralTokenException()


    def get_vote_for_user(self, user):
        """Return vote for user on this action.

        raises Vote.DoesNotExist"""
        
        return self.votes.get(user=user)
        
    def vote_add(self, user, referral=None):
        return askbot_extensions.utils.vote_add(self.question, user, referral)

    def comment_add(self, comment, user):
        """ Have to check for:
        
            1- user login --> in the Views
            2- action status (has to not be draft)
        
            added_at and by_email are handled by post.add_comment
        """

        self.question.add_comment(comment, 
            user, 
            added_at=None, 
            by_email=False
        )
        
        log.debug("Comment added for user %s on action %s" % (
            user, self
        ))

    def blog_post_add(self, text, user):
        """ Add a blog post to an Action. """

        Post.objects.create_new_answer(thread=self.thread,
            author=user,
            added_at=datetime.datetime.now(),
            text=text,
            wiki=False,
            email_notify = False,
            by_email = False
        )

        log.debug("Blog post added for user %s on action %s" % (
            user, self
        ))
    
    def users_impact_factor(self):
        """Return a User queryset with annotation of action impact factor"""
        # TODO: TOCACHE
        return action.voters.annotate(local_impact_factor=models.Count('votes'))


#WAS: This method is confusing: you do not need to know Action to comment a blog post.
#WAS: Pretending to know action AND blog post could lead to incoherent situation.
#WAS: If there is no needing to know a detail to do something, don't ask for the detail.
#WAS:    def blogpost_comment_add(self, blogpost, comment, user):
#WAS:        """ Have to check for:
#WAS:        
#WAS:            1- user login --> in the Views
#WAS:            2- action status (has to not be draft)
#WAS:        
#WAS:            added_at and by_email are handled by post.add_comment
#WAS:        """
#WAS:
#WAS:        blogpost.add_comment(comment, 
#WAS:            user, 
#WAS:            added_at=None, 
#WAS:            by_email=False
#WAS:        )
#WAS:        
#WAS:        log.debug("Comment added for user %s on blog article %s" % (
#WAS:            user, blogpost
#WAS:        ))
        

#--------------------------------------------------------------------------------

class Geoname(models.Model):

    #COMMENT LF: we do not restrict CharField choices
    # in order to support versatile API
    # GEO_CHOICES = (
    #     ('state', 'Stato'),
    #     ('province', 'Provincia'),
    #     ('municipality', 'Comune'),
    # )

    name = models.CharField(max_length=512)
    kind = models.CharField(max_length=64) #, choices=GEO_CHOICES)

    # Modifier for threshold computation
    threshold_factor = models.FloatField(default=1)

    external_resource = models.OneToOneField(ExternalResource)

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.kind)

    class Meta:
        unique_together = (('name','kind'),)

#--------------------------------------------------------------------------------

class ActionCategory(models.Model, Resource):

    # The name is in the form MAINCATEGORY::SUBCATEGORY
    # accept arbitrary sublevels

    name = models.CharField(max_length=128, unique=True, blank=False,verbose_name=_('name'))
    description = models.TextField(blank=True,verbose_name=_('description'))
    #image = models.ImageField(upload_to=get_resource_icon_path, null=True, blank=True,verbose_name=_('image'))
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name=_('Product category')
        verbose_name_plural = _("Product categories")
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
    @property
    def icon(self):
        return self.image or super(ActionCategory, self).icon


#--------------------------------------------------------------------------------

class Politician(models.Model):
    pass

#--------------------------------------------------------------------------------

class Media(models.Model):
    pass

#--------------------------------------------------------------------------------
# Askbot signal handling

from django.db.models.signals import post_save
from django.dispatch import receiver

#WAS: @receiver(post_save, sender=Thread)
#WAS: def create_action(sender, **kwargs):
#WAS:     if kwargs['created']:
#WAS:         thread = kwargs['instance']
#WAS:         try:
#WAS:             assert(thread.action)
#WAS:         except Action.DoesNotExist as e:
#WAS:             action = Action(
#WAS:                 thread = thread,
#WAS:                 created_by = thread.question.author
#WAS:             )
#WAS:             action.save()

@receiver(post_save, sender=Post)
def create_action(sender, **kwargs):
    if kwargs['created']:
        post = kwargs['instance']
        if post.is_question():
            action = Action(
                thread = post.thread,
                created_by = post.author
            )
            action.save()
            
