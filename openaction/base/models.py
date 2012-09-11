from django.db import models

from lib import ClassProperty
from django.db.models import permalink

import logging
log = logging.getLogger(__name__)

class Resource(object):
    """Base class for project fundamental objects.

    This is a basic mix-in class used to factor out data/behaviours common
    to the majority of model classes in the project's applications.
    
    Resource API is composed of:
    * Basic methods and properties: 
     * basic type and resource string representation
     * caching operations
    * Relational properties:
     * how the resource relates to other resources
    """

    # Attribute used to make a list of confidential lists
    confidential_fields = ()

    # Attribute used to cache data
    volatile_fields = []

    #-----------------------------------------
    # Basic properites
    #-----------------------------------------

    @ClassProperty
    @classmethod
    def resource_type(cls):
        """String representation of resource type"""
        
        return cls.__name__.lower()

    @property
    def urn(self):
        """Unique resource name"""
        return '%s/%s' % (self.resource_type, self.pk)
    
    @property
    def ancestors(self):
        """List of ancestors of a resource.

        This is te list of parents from root to the resource itself.
        It is used p.e. to display navigation breadcrumbs.

        You SHOULD NOT implement it in subclasses
        """
        
        if self.parent:
            return self.parent.ancestors + [self.parent]
        else:
            return []

    @property
    def parent(self):
        """Identifies resource which includes this resource.

        Stated that there can be only one parent for a resource,
        (no multiple parents allowed), setting this attribute makes the resource
        confident of who includes itself.

        This attribute is then used to make the list of `:ref:ancestors`.
        
        You MUST implement it in subclasses if they have parent.
        """
        return None

    @property
    def comments(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        notes = Comment.objects.filter(object_pk=self.pk, content_type=ctype).order_by('-submit_date')
        return notes

    @permalink
    def get_absolute_url(self):
        return ('rest.views.resource_page', (), { 
                'resource_type' : self.resource_type, 
                'resource_id' : self.pk 
        })

    #def get_absolute_url_page(self):
    #    return self.get_absolute_url().replace('/rest', '/rest/#rest')

    def as_dict(self):
        return {
            'name': unicode(self),
            'urn' : self.urn,
        }

    @classmethod    
    def cache_key(cls, id):
        #The cache key is used for key management    
		return "%s/%s" % (cls.__name__.lower(), id)


    @property
    def icon(self):
        "Returns default icon for resource"""
        icon = models.ImageField(upload_to="fake")
        basedir = os.path.join(settings.MEDIA_URL, "nui", "img", settings.THEME)
        icon.url = os.path.join(basedir, "%s%s.%s" % (self.resource_type, "128x128", "png"))
        return icon

