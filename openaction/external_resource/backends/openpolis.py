
from django.http import HttpResponse

from external_resource.backends import base

import json, urllib2, base64, urlparse

#--------------------------------------------------------------------------------

class OpenPolisResourceBackend(base.CachedResourceBackend):

    def get_url(self, url):
        """Retrieve an url, return http response"""

        full_url = self.base_url + url
        data = self.get_data(full_url, as_string=True)
        return HttpResponse(data, mimetype="application/json")

    def get_data(self, full_url, as_string=False):
        """Retrieve data from cache or from url, cache result, return data

        param:as_string set it to True if you want data to be returned as plaintext.
        """

        data = self.get_from_cache(full_url)

        if not data:
            # Retrieve data
            request = urllib2.Request(full_url)
            base64string = base64.standard_b64encode('%s:%s' % (self.username, self.password))
            request.add_header("Authorization", "Basic %s" % base64string)   
            result = urllib2.urlopen(request)
            data = result.read()
            self.save_in_cache(full_url, data)

        if not as_string:
            data = json.load(data)

        return data

#--------------------------------------------------------------------------------

class OpenPolisLocationsBackend(OpenPolisResourceBackend):

    def get_url(self, url):
        url = 'locations/' + url
        return super(OpenPolisLocationsBackend, self).get_url(url)

    def get_info(self, resource):
        """Call OpenPolis API and return normalized data."""

        rel_url = 'locations/' + resource.id + '/'
        location_detail_url = urlparse.urljoin(self.base_url, rel_url)
        location_data = self.get_data(location_detail_url)

        rel_url = 'cityreps/op_id/' + resource.id + '/'
        city_reps_url = urlparse.urljoin(self.base_url, rel_url)
        city_reps_data = self.get_data(city_reps_url)

        normalized_data = data.update(city_reps_data)

        #normalized_data = {
        #    'id' : data.get('id'),
        #    'name' : data.get('name'),
        #    'email' : data.get('email'),
        #    'username' : data.get('username'),
        #}

        return normalized_data
