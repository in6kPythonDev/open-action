from django.db import models
from django.core.urlresolvers import reverse

from askbot.models import User
from external_resource.models import ExternalResource

class Organization(models.Model):

    name = models.CharField(max_length=256)
    external_resource = models.ForeignKey(ExternalResource, null=True)
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    @property
    def representatives(self):
      return self.user_set.filter(is_representative=True) 

    @property
    def followers(self):
      return self.user_set.filter(is_follower=True)

    def get_absolute_url(self):
        return reverse("org-detail", args=(self.pk,))

#--------------------------------------------------------------------------------

class UserOrgMap(models.Model):

    user = models.ForeignKey(User, related_name="organization_set")
    org = models.ForeignKey(Organization, related_name="user_set")
    grant_privacy_access = models.BooleanField(default=False)
    is_representative = models.BooleanField(default=False)
    is_follower = models.BooleanField(default=False)

    def __unicode__(self):
        return u"Relation between user %s and organization %s" % (self.user, 
    self.org)

    
    class Meta:
        unique_together = (('user', 'org'),)
