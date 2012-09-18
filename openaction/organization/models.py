from django.db import models
from askbot.models import User

from external_resource.models import ExternalResource

class Organization(models.Model):

    name = models.CharField(max_length=256)
    external_resource = models.ForeignKey(ExternalResource)
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    @property
    def representatives(self):
      return self.user_set.filter(is_representative=True) 

#--------------------------------------------------------------------------------

class UserOrgMap(models.Model):

    user = models.ForeignKey(User)
    org = models.ForeignKey(Organization, related_name="user_set")
    grant_privacy_access = models.BooleanField(default=False)
    is_representative = models.BooleanField(default=False)
    is_follower = models.BooleanField(default=False)

    def __unicode__(self):
        return u"Relation between user %s and organization %s" % (self.user, 
    self.org)

    
