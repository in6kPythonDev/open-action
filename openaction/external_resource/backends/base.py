
from django.http import HttpResponse

from lib.cache import Store as oa_cache

import json, urllib2, base64, time, urlparse

class ExternalResourceBackend(object):

    def __init__(self, settings_dict):
        super(ExternalResourceBackend, self).__init__()
        self.settings_dict = settings_dict
        self.base_url = urlparse.urlunsplit((
            settings_dict['PROTOCOL'],
            "%s:%s" % (settings_dict['HOST'], settings_dict['PORT']),
            settings_dict['BASE_PATH'],
            '', ''
        ),)
        self.username = self.settings_dict['USER']
        self.password = self.settings_dict['PASSWORD']

    def get_external_info(self, resource):
        """Dispatcher to real getter method for specific resource type.

        Default machinery calls get_<resource_type>_info method
        """

        try:
            method_name = "get_%s_info" % resource.ext_res_type
        except KeyError as e:
            raise NotImplementedError(
                "Backend %s method to retrieve external info for a %s" % (
                self.__class__.__name__, resource.ext_res_type
            ))
        return getattr(self, method_name)(resource)


class CachedResourceBackend(ExternalResourceBackend):

    CACHE_REFRESH_INTERVAL = 10000

    def get_from_cache(self, full_url):

        key = self.cache_key(full_url)
        cached_entry = oa_cache.get(key)
        rv = None
        if cached_entry:
            if self.cached_entry_is_valid(cached_entry):
                rv = cached_entry['data']

        return rv

    def save_in_cache(self, full_url, data):

        key = self.cache_key(full_url)
        oa_cache.set(key, { 
            'timestamp' : int(time.time()),
            'data' : data 
        })
        return True

    @classmethod
    def cache_key(cls, url):
        return url
        #return "%s-%s" % (cls.__name__.lower(), url)

    def cached_entry_is_valid(self, cached_entry):

        timestamp = cached_entry['timestamp']
        return int(time.time()) - timestamp < self.CACHE_REFRESH_INTERVAL

#--------------------------------------------------------------------------------

class FBResourceBackend(ExternalResourceBackend):

    def get_auth_querystring(self):
        # Use OpenAction access token to build querystring (see: social auth)
        return "TODO"

    def do_request(self, destination):
        """Given a destination (usually a URL), manage authentication if needed."""

        url = destination
        url += "&%s" % self.get_auth_querystring()
        response = urllib2.open(url)
        raw_data = response.read()
        return raw_data

    def get_user_info(self, resource):
        """Call Facebook API and return normalized data."""

        fields = ['id','name','email', 'username']
        auth_qs = self.get_auth_querystring()

        graphapi_url = "https://graph.facebook.com/%s?fields=%s&format=json&%s" % (self.id, ",".join(fields), auth_qs)

        raw_data = self.do_request(graphapi_url)
        data = json.load(raw_data)
        
        normalized_data = {
            'id' : data.get('id'),
            'name' : data.get('name'),
            'email' : data.get('email'),
            'username' : data.get('username'),
        }

        return normalized_data

