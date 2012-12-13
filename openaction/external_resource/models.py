# Author: Luca Ferroni <luca@befair.it>
# License: AGPLv3

from django.db import models
from django.conf import settings

from base.models import Resource
from askbot_extensions.models import User

from lib import load_symbol
from lib.djangolib import ModelExtender

from external_resource import utils

import datetime, pickle

class ExternalResource(models.Model):
    """Registry of external resources."""

    backend_name = models.CharField(max_length=64, verbose_name=u"nome del backend",
        help_text=u"nome convenzionale che comprende l'api del backend da chiamare"
    )

    ext_res_id = models.CharField(max_length=1024, verbose_name="id della risorsa nel backend")
    ext_res_type = models.CharField(max_length=128, verbose_name="tipo della risorsa nel backend")
    first_get_on = models.DateTimeField(verbose_name="FIRST", auto_now_add=True)
    last_get_on = models.DateTimeField(verbose_name="LAST", auto_now=True)

    # is_valid is used to force cache reload
    is_valid = models.BooleanField(default=True)
    # is_deleted is used to say that this resource does not exist anymore
    is_deleted = models.BooleanField(default=True)

    # pickled data to cache additional info
    # It is a pickled dictionary. It has key 'external_info'
    # TODO: NoSQL cache
    _data = models.TextField()

    class Meta:
        app_label = "external_resource"

    def __unicode__(self):
        return u"%s - %s" % (self.backend_name, self.ext_res_id)

    @property
    def ext_unique_id(self):
        """Unique id: it may be overridden by 'proxy' subclasses for specific resources if needed."""
        return self.ext_res_id

    @property
    def external_info(self):
        # TODO: NoSQL cache
        #key = self.__class__.cache_key(self.id)
        #data = pstore.getalldata(key, 'external_info')
        #return data['external_info']
        rv = None
        if self._data:
            data = pickle.loads(self._data)
            rv = data.get('external_info')

        if not rv:
            # Retrieve external_info from backend
            backend = self.get_backend()
            rv = backend.get_external_info(self)

            # TODO: Check results!
            # case 1: got results
            # case 2: network error
            # case 3: user has not autorized access to resource
            if 1: #TODO: Check results!

                if not self._data:
                    self.first_get_on = datetime.datetime.now()

                self.last_get_on = datetime.datetime.now()

                # Cache data retrieved
                self.external_info = rv

                self.save()

        return rv

    @external_info.setter
    def cache_external_info(self, value):
        # TODO: NoSQL cache
        #key = self.__class__.cache_key(self.id)
        #data = pstore.savedata(key, { 'external_info' : value })
        #return data['external_info']
        new_data = { 'external_info' : value }
        if self._data:
            data = pickle.loads(self._data)
        else:
            data = {}
        data.update(new_data)
        self._data = pickle.dumps(data)

    def get_backend(self):
        return utils.load_backend(self.backend_name)

    @property
    def backend(self):
        try:
            assert self.__backend
        except AttributeError as e:
            self.__backend = self.get_backend()

        return self.__backend

    def update_external_data(self, lookup, _id, datum):
        """ Invalidate redis cache and update it with new data """

        url = "%s%s" % (self.backend.base_url,lookup.get_url(_id))
        self.backend.save_in_cache(
            url,
            datum
        )

#-------------------------------------------------------------------------------------

class UserExternalResourceExtension(ModelExtender):

    ext_prefix = '_askbot_ext_'

    def _askbot_ext_get_external_info(self, social_auth_backend_name, attrs=[]):
        return {} #TODO fero TOSEE
        """Retrieve external info from external resource"""

        from external_resource.models import ExternalResource

        # Use "social_auth" to get the bound external_id for the specific backend
        external_id = 1 #TODO: Social auth user association for specific backend
        #WAS: backend_name=settings.SOCIAL_AUTH_TO_EXTERNAL_RESOURCE_BACKEND_MAP[backend_name]
        backend_name=settings.SOCIAL_AUTH_TO_EXTERNAL_RESOURCE_BACKEND_MAP[social_auth_backend_name]
        external_resource = ExternalResource.objects.get(
            backend_name=backend_name, ext_res_id=external_id
        )

        return external_resource.external_info

User.add_to_class('ext_noattr', UserExternalResourceExtension())

