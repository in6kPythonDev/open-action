from django.utils.html import escape

from ajax_select import LookupChannel

from external_resource import utils
from action.models import Geoname, Politician
from action import exceptions

import json, datetime, urlparse
from cgi import escape

class GeonameDict(dict):

    def __init__(self, pk, **kwargs):
        self.pk = pk
        super(GeonameDict, self).__init__(**kwargs)

class GeonameLookup(LookupChannel):

    model = Geoname

    def get_query(self,q,request):
        # I will use this logic in the get_objects too:
        # I will get a list of structures containing the Json data,
        # that will be used into the Action view
        backend_name = self.get_backend_name()
        backend = utils.load_backend(backend_name)
        full_url = backend.base_url + "locations/?namestartswith=%s" % q
        data = backend.get_data(full_url)
        fake_qs = []
        for d in data:
            backend_name = "cityreps"
            backend = utils.load_backend(backend_name)
            rel_url = 'cityreps/op_id/' + str(d["id"]) + '/'
            city_reps_url = urlparse.urljoin(backend.base_url, rel_url)
            city_reps_data = backend.get_data(city_reps_url)
            d.update(city_reps_data)
            fake_qs.append(GeonameDict(d["id"], **d))
        return fake_qs
 
    #WAS: def get_objects(self, ids):
    #WAS:     """ Return a list of structures containing Json data """

    #WAS:     #was:  backend_name = "locations"
    #WAS:     backend_name = self.get_backend_name()
    #WAS:     backend = utils.load_backend(backend_name)

    #WAS:     json_data = []
    #WAS:     for _id in ids:
    #WAS:         full_url = backend.base_url + "locations/%s" % _id
    #WAS:         data = backend.get_data(full_url)
    #WAS:         j_data = GeonameDict(data["id"], **data)
    #WAS:         #'data' will surely contain a Json object
    #WAS:         if len(j_data) == 0:
    #WAS:             raise exceptions.ParanoidException()
    #WAS:         else:
    #WAS:             json_data.append(j_data)
    #WAS:     return json_data
    def get_objects(self, ids):
        """ Return a list of structures containing Json data """

        backend_name = self.get_backend_name()
        backend = utils.load_backend(backend_name)

        json_data = []
        for _id in ids:
            data = backend.get_info(_id)
            j_data = GeonameDict(data["id"], **data)
            json_data.append(j_data)

        return json_data

    #def get_result(self,obj):
    #    log.debug(obj,"BBBBBB")
    #    return unicode(obj)

    def get_backend_name(self):
        """ Return the name of this LookupChannel backend """
        return "locations"
 
    def format_match(self,obj):
        #return obj["name"]
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        
        return u"<div><i>%s</i> (%s)</div>" % (escape(obj["name"]),obj["id"])
#        values = (escape(obj.name),escape(obj.zipcode),escape(obj.city))
#        format = u"%s - %s %s"
#        if len(obj.province) > 0:
#            values = values + (escape(obj.province),) # the final , forces tuple concatenation -FS
#            format += " (%s)"
#            
#        #log.debug("values=", values)    
#            
#        return format % values 

    def can_add(self,user,model):
        """ customize can_add by allowing anybody to add a Group.
            the superclass implementation uses django's permissions system to check.
            only those allowed to add will be offered a [+ add] popup link
            """
        return False

    def check_auth(self, request):
        """ The superclass implementation raises exception if the request
        user is not a staff member """

        if not request.user.is_authenticated():
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied

    def get_url(self, _id=None):

        if _id:
            return "locations/%s/" % _id
        return "locations/"

    def get_result(self,obj):
        """ Override default unicode(obj), to allow json.dumps """
        return obj


class CityrepLookup(LookupChannel):

    def get_objects(self, ids):
        """ Return a list of structures containing Json data """

        #was:  backend_name = "locations"
        backend_name = self.get_backend_name()
        backend = utils.load_backend(backend_name)

        json_data = []
        for _id in ids:
            j_data = backend.get_info(_id)
            json_data.append(j_data)

        return json_data
        
    def get_backend_name(self):
        """ Return the name of this LookupChannel backend """
        return "cityreps"

    def check_auth(self, request):
        """ The superclass implementation raises exception if the request
        user is not a staff member """

        if not request.user.is_authenticated():
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied

    def get_url(self, _id=None):

        if _id:
            return "cityreps/%s/" % _id
        return "cityreps/"

class PoliticianLookup(LookupChannel):

    def get_objects(self, ids):
        """ Return a list of structures containing Json data """

        #was:  backend_name = "locations"
        backend_name = self.get_backend_name()
        backend = utils.load_backend(backend_name)

        json_data = []
        for _id in ids:
            j_data = backend.get_info(_id)
            json_data.append(j_data)

        return json_data
        
    def get_backend_name(self):
        """ Return the name of this LookupChannel backend """
        return "politicians"

    def check_auth(self, request):
        """ The superclass implementation raises exception if the request
        user is not a staff member """

        if not request.user.is_authenticated():
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied

    def get_url(self, _id=None):

        if _id:
            return "politicians/%s/" % _id
        return "politicians/"

#class PersonLookup(LookupChannel):
#
#    model = Person
#
#    def get_query(self,q,request):
#        qs = Person.objects.filter(name__icontains=q)
#        qs |= Person.objects.filter(surname__icontains=q)
#        qs |= Person.objects.filter(display_name__icontains=q)
#        return qs.order_by('surname','name')[:10]
#
##    def get_result(self,obj):
##        log.debug(obj,"BBBBBB")
##        return unicode(obj)
#        
#    def format_match(self,obj):
#        return self.format_item_display(obj)
#
#    def format_item_display(self,obj):
#        try:
#            url = obj.avatar.url
#        except ValueError as e:
#            url = ""
#        
#        return u'<img src="%s" /> %s' % (url, escape(unicode(obj)))
#
#    def can_add(self,user,model):
#        """ customize can_add by allowing anybody to add a Group.
#            the superclass implementation uses django's permissions system to check.
#            only those allowed to add will be offered a [+ add] popup link
#            """
#        return True
