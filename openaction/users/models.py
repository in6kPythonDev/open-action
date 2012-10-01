#LF Taken and modified from OpenMunicipio

from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from model_utils import Choices
import sys

#LF from open_municipio.monitoring.models import Monitoring
#LF from open_municipio.newscache.models import News
#LF from open_municipio.people.models import Person


class UserProfile(models.Model):
    """
    This model describes a user's profile.
    
    All infos about a user are here, except for those already in ``auth.User``,
    that is: 
    
     * ``username``
     * ``password`` 
     * ``first_name``, ``last_name``, ``email``
     * ``is_staff``, ``is_active``, ``is_superuser``
     * ``last_login``, ``date_joined``
    
    In order to enable user profile management, Django settings file must contain this option:
    
        ``AUTH_PROFILE_MODULE = 'users.UserProfile'``


    Usage notes
    -----------
    
    * From user to profile: ``user.get_profile()``
    * From profile to user: ``profile.user``

    """
    PRIVACY_LEVELS = Choices(
        (1, 'all', _('all')),
        (2, 'some', _('some')),
        (3, 'none', _('none'))
    )

    # This field is required.
    user = models.OneToOneField(User)
    
    # the user wants to be identified through his nickname,
    # his name will never be shown publicly in the web site
    uses_nickname = models.BooleanField(_('show my nickname, not my name'), default=False)
    
    # the user has declared to be a politician in the registration phase
    # this needs to be verified, before assigning the user to the *Politicians* group
    # and linking the user's profile to a Person instance
    says_is_politician = models.BooleanField(_('i am a politician'), default=False)
    #LF person = models.OneToOneField(Person, blank=True, null=True)

    # user's privacy options
    privacy_level = models.IntegerField(_('privacy level'), choices=PRIVACY_LEVELS, default=PRIVACY_LEVELS.none)
    
    # the user wants to receive newsletters (whatever that means)
    wants_newsletter = models.BooleanField(_('wants newsletter'), default=False)
    
    # TODO: ``city`` must be a foreign key to a proper, dedicated table of locations
    city = models.CharField(_(u'location'), max_length=128)

    #LF # manager to handle the list of news that have the act as related object
    #LF related_news_set = generic.GenericRelation(News,
    #LF                                         content_type_field='related_content_type',
    #LF                                        object_id_field='related_object_pk')

    description = models.TextField(blank=True)
    home_page = models.URLField(blank=True, verify_exists=True, verbose_name="sito web")

    class Meta:
        db_table = u'users_user_profile'

    def __unicode__(self):
        return self.public_name

    @permalink
    def get_absolute_url(self):
        return 'profiles_profile_detail', (), { 'username': self.user.username }

    @property
    def public_name(self):
        """
        Returns the public user name, based on the uses_nickname flag
        """
        if  self.uses_nickname:
            return self.user.username
        else:
            return self.user.get_full_name()

    #LF @property
    #LF def related_news(self):
    #LF     """
    #LF     Returns the related_news_set as a list of objects
    #LF     """
    #LF     return self.related_news_set.all()

    #LF @property
    #LF def monitored_objects(self):
    #LF     """
    #LF     Returns objects monitored by this user (as a list).
    #LF     """
    #LF     return [o.content_object for o in Monitoring.objects.filter(user=self.user)]

    #LF def is_editor(self):
    #LF     try:
    #LF         self.user.groups.get(name='editors')
    #LF         return True
    #LF     except ObjectDoesNotExist:
    #LF         return False



