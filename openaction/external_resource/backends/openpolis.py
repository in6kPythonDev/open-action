
from django.http import HttpResponse

from external_resource.backends import base

import json, urllib2, base64, urlparse

#--------------------------------------------------------------------------------

class OpenPolisResourceBackend(base.CachedResourceBackend):

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
            data = json.loads(data)

        return data

#--------------------------------------------------------------------------------

class OpenPolisLocationsBackend(OpenPolisResourceBackend):

    def get_url(self, url, request):
        url = 'locations/' + url
        return super(OpenPolisLocationsBackend, self).get_url(url, request)

    def get_info(self, resource):
        """Call OpenPolis API and return normalized data."""

        rel_url = 'locations/' + resource.id + '/'
        location_detail_url = urlparse.urljoin(self.base_url, rel_url)
        location_data = self.get_data(location_detail_url)

        rel_url = 'cityreps/op_id/' + resource.id + '/'
        city_reps_url = urlparse.urljoin(self.base_url, rel_url)
        city_reps_data = self.get_data(city_reps_url)

        normalized_data = location_data.update(city_reps_data)

        #normalized_data = {
        #    'id' : data.get('id'),
        #    'name' : data.get('name'),
        #    'email' : data.get('email'),
        #    'username' : data.get('username'),
        #}

        return normalized_data

class OpenPolisPoliticiansBackend(OpenPolisResourceBackend):

    def get_url(self, url, request):
        url = 'politicians/' + url
        return super(OpenPolisPoliticiansBackend, self).get_url(url, request)

    def get_info(self, resource):
        """Call OpenPolis API and return normalized data."""

        rel_url = 'politicians/' + str(resource)
        location_detail_url = urlparse.urljoin(self.base_url, rel_url)
        #print("\nlocation_detail_url: %s" %  location_detail_url)
        location_data = self.get_data(location_detail_url)

        normalized_data = location_data
        #print("\nlocations_data: %s\n" % normalized_data)

        #normalized_data = {
        #    'id' : data.get('id'),
        #    'name' : data.get('name'),
        #    'email' : data.get('email'),
        #    'username' : data.get('username'),
        #}

        return normalized_data

class OpenPolisCityrepsBackend(OpenPolisResourceBackend):

    def get_url(self, url, request):
        url = 'cityreps/op_id/' + url
        return super(OpenPolisCityrepsBackend, self).get_url(url, request)

    def get_info(self, resource):
        """Call OpenPolis API and return normalized data."""

        rel_url = 'cityreps/op_id/' + str(resource) + '/'

        city_reps_url = urlparse.urljoin(self.base_url, rel_url)
        city_reps_data = self.get_data(city_reps_url)

        normalized_data = city_reps_data
#        print("\ncity_reps_data: %s\n" % normalized_data['city_representatives'])
        #normalized_data = {
        #    'id' : data.get('id'),
        #    'name' : data.get('name'),
        #    'email' : data.get('email'),
        #    'username' : data.get('username'),
        #}

        return normalized_data
