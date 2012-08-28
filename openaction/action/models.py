from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

from askbot.models import Thread
from askbot.models.post import Post

from base.models import Resource
from base.utils import get_resource_icon_path
from action import const

class Action(models.Model, Resource):

    # Extending Askbot model!
    thread = models.OneToOneField(Thread)

    victory = models.BooleanField(default=False)

    threshold = models.PositiveIntegerField(blank=True, null=True)

    geoname_set = models.ManyToManyField('Geoname', null=True, blank=True)
    category_set = models.ManyToManyField('ActionCategory', null=True, blank=True)

    # Status can be 
    # CREATED, DRAFT, CANCELED DRAFT, ACTIVE, CLOSED, VICTORY
    @property
    def status(self):

        if self.victory:
            status = const.ACTION_STATUS['victory']
        elif self.thread.closed:
            status = const.ACTION_STATUS['closed']
        elif self.question.deleted:
            status = const.ACTION_STATUS['deleted']
        elif self.score == 0:
            # cannot be voted until all fields are set
            # so the Action goes into "ready" status
            status = const.ACTION_STATUS['draft']
        elif not self.threshold or self.score < self.threshold:
            status = const.ACTION_STATUS['ready']
        elif self.score >= self.threshold:
            status = const.ACTION_STATUS['active']
        return status

    @property
    def question(self):
        """QUestion holds the main content for an action.

        It is an askbot Post of type ``question``
        """
        #DONE: moved in askbot_models_extension
        return self.thread.question
        

    @property
    def owner(self):
        ''' 
            The owner is the User who posted this action
            question. 
        '''
        #WAS: post = self.thread.posts.get(post_type='question')
        #WAS: return post.author
        return self.question.author

    @property
    def pingbacks(self):
        pass

    @property
    def create_datetime(self):
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
        if self.status != const.ACTION_STATUS['active']:
            status = u" [%s]" % self.status
        return u"%s%s" % (self.thread.title, status)
    

    @property
    def description(self):
        """Description is a quite short summary of the action"""

        # TODO TOTHINK 
        # Askbot summary is 300 chars long, we should enlarge it...
        return self.question.summary
    
    @property
    def score(self):
        return self.question.score

    @property
    def content(self):
        return self.question.text

    @property
    def votes(self):
        return self.question.votes

    @property
    def voters(self):
        return self.votes.values('user__username').order_by('-voted_at') 

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

#--------------------------------------------------------------------------------

class Geoname(models.Model):

    GEO_CHOICES = (
        ('state', 'Stato'),
        ('province', 'Provincia'),
        #TODO: Matteo
    )

    name = models.CharField(max_length=1024)
    kind = models.CharField(max_length=32, choices=GEO_CHOICES)

    # Modifier for threshold computation
    threshold_factor = models.FloatField(default=1)

#--------------------------------------------------------------------------------

class ActionCategory(models.Model, Resource):

    # The name is in the form MAINCATEGORY::SUBCATEGORY
    # accept arbitrary sublevels

    name = models.CharField(max_length=128, unique=True, blank=False,verbose_name=_('name'))
    description = models.TextField(blank=True,verbose_name=_('description'))
    #image = models.ImageField(upload_to=get_resource_icon_path, null=True, blank=True,verbose_name=_('image'))

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
# Askbot signal handling

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Thread)
def create_action(sender, **kwargs):
    if kwargs['created']:
        action = Action(thread=kwargs['instance'])
        action.save()
