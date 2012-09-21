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
        users_pk = self.usermap_set.filter(is_representative=True).values_list('user__pk', flat=True)
        return User.objects.filter(pk__in=users_pk) 

    @property
    def followers(self):
        users_pk = self.usermap_set.filter(is_follower=True).values_list('user__pk', flat=True)
        return User.objects.filter(pk__in=users_pk) 

    def get_absolute_url(self):
        return reverse("org-detail", args=(self.pk,))

#--------------------------------------------------------------------------------

class UserOrgMap(models.Model):

    user = models.ForeignKey(User, related_name="orgmap_set")
    org = models.ForeignKey(Organization, related_name="usermap_set")
    grant_privacy_access = models.BooleanField(default=False, help_text="l'utente consente all'associazione di accedere ai propri dati personali memorizzati in Open Action")
    is_representative = models.BooleanField(default=False, help_text="l'utente rappresenta l'associazione")
    is_follower = models.BooleanField(default=False, help_text="l'utente segue l'associazione")

    def __unicode__(self):
        return u"Relation between user %s and organization %s" % (self.user, self.org)

    
    class Meta:
        unique_together = (('user', 'org'),)
