
from django.http import HttpResponse

from external_resource.backends import base

import json, urllib2, base64, urlparse

#--------------------------------------------------------------------------------

class OpenPolisResourceBackend(base.CachedResourceBackend):

    def get_data(self, full_url, as_string=False, del_from_cache=False):
        """Retrieve data from cache or from url, cache result, return data

        param:as_string set it to True if you want data to be returned as plaintext.
        """

        if del_from_cache:
            self.delete_from_cache(full_url)
            data = None
        else:
            data = self.get_from_cache(full_url)

        if not data:
            # Retrieve data
            request = urllib2.Request(full_url)
            base64string = base64.standard_b64encode('%s:%s' % (self.username, self.password))
            request.add_header("Authorization", "Basic %s" % base64string)   
            result = urllib2.urlopen(request)
            data = result.read()
            self.save_in_cache(full_url, data)

        if not as_string and isinstance(data, basestring):
            data = json.loads(data)

        return data

#--------------------------------------------------------------------------------

class OpenPolisLocationsBackend(OpenPolisResourceBackend):

    def get_url(self, url, request):
        url = 'locations/' + url
        return super(OpenPolisLocationsBackend, self).get_url(url, request)

    def get_info(self, resource):
        """Call OpenPolis API and return normalized data."""

        rel_url = 'locations/' + str(resource) + '/'
        location_detail_url = urlparse.urljoin(self.base_url, rel_url)
        #WAS: location_data = self.get_data(location_detail_url)
        try:
            location_data = self.get_data(location_detail_url)
        except TypeError as e:
            location_data = self.get_data(location_detail_url,
                del_from_cache=True
            )

        #KO: rel_url = 'cityreps/op_id/' + str(resource) + '/'
        #KO: city_reps_url = urlparse.urljoin(self.base_url, rel_url)
        #KO: city_reps_data = self.get_data(city_reps_url)

        #KO: location_data.update(city_reps_data)

        #normalized_data = {
        #    'id' : data.get('id'),
        #    'name' : data.get('name'),
        #    'email' : data.get('email'),
        #    'username' : data.get('username'),
        #}

        #return normalized_data
        return location_data

class OpenPolisPoliticiansBackend(OpenPolisResourceBackend):

    INSTITUTIONS = {
        'comune' : ['consiglio','giunta',],
        'provincia' : ['consiglio','giunta',],
        'regione' : ['consiglio','giunta',],
        'senato' : ['representatives',],
        'europarl' : ['representatives',],
        'camera' : ['representatives',],
    }

    def get_url(self, url, request):
        url = 'politicians/' + url
        return super(OpenPolisPoliticiansBackend, self).get_url(url, request)

    def get_info(self, resource):
        """Call OpenPolis API and return normalized data."""

        rel_url = 'politicians/' + str(resource)
        politician_detail_url = urlparse.urljoin(self.base_url, rel_url)
        #print("\npolitician_detail_url: %s" %  location_detail_url)
        #WAS: location_data = self.get_data(location_detail_url)
        try:
         politician_data = self.get_data(politician_detail_url)
        except TypeError as e:
            politician_data = self.get_data(politician_detail_url,
                del_from_cache=True
            )

        normalized_data = politician_data
        #print("\nlocations_data: %s\n" % normalized_data)

        #normalized_data = {
        #    'id' : data.get('id'),
        #    'name' : data.get('name'),
        #    'email' : data.get('email'),
        #    'username' : data.get('username'),
        #}

        return normalized_data

    #def get_info(self, cityrep, resource):
    #    """Call OpenPolis API and return normalized data."""

    #    rel_url = 'cityreps/op_id/' + str(cityrep) + '/'
    #    cityrep_url =  urlparse.urljoin(self.base_url, rel_url)

    #    cityrep_data = self.get_data(cityrep_url)

    #    politician_id = 0
    #    for institution, institution_kinds in self.INSTITUTIONS.items():

    #        for inst_kind in institution_kinds:
    #            cityreps_of_kind = cityrep_data[institution][inst_kind]

    #            for politician in cityreps_of_kind:
    #                if politician['charge_id'] in charge_ids:
    #                    politician_id = politician['politician_id']
    #                    break
    #            if politician_id:
    #                break
    #        if politician_id:
    #            break

    #    rel_url = 'politicians/' + str(politician_id)
    #    location_detail_url = urlparse.urljoin(self.base_url, rel_url)

    #    location_data = self.get_data(location_detail_url)

    #    normalized_data = location_data

    #    return normalized_data

class OpenPolisCityrepsBackend(OpenPolisResourceBackend):

    def get_url(self, url, request):
        url = 'cityreps/op_id/' + url
        return super(OpenPolisCityrepsBackend, self).get_url(url, request)

    def get_info(self, resource):
        """Call OpenPolis API and return normalized data."""

        rel_url = 'cityreps/op_id/' + str(resource) + '/'

        city_reps_url = urlparse.urljoin(self.base_url, rel_url)
        #WAS: city_reps_data = self.get_data(city_reps_url)
        try:
         city_reps_data = self.get_data(city_reps_url)
        except TypeError as e:
            city_reps_data = self.get_data(city_reps_url,
                del_from_cache=True
            )

        normalized_data = city_reps_data
        #print("\ncity_reps_data: %s\n" % normalized_data['city_representatives'])
        #normalized_data = {
        #    'id' : data.get('id'),
        #    'name' : data.get('name'),
        #    'email' : data.get('email'),
        #    'username' : data.get('username'),
        #}

        return normalized_data
