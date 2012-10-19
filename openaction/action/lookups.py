from django.utils.html import escape

from ajax_select import LookupChannel

from external_resource import utils
from action.models import Geoname

import json
from cgi import escape

class GeonameDict(dict):

    def __init__(self, pk, **kwargs):
        self.pk = pk
        super(GeonameDict, self).__init__(**kwargs)

class GeonameLookup(LookupChannel):

    model = Geoname

    def get_query(self,q,request):

        backend_name = "locations"
        backend = utils.load_backend(backend_name)
        full_url = backend.base_url + "locations/?namestartswith=%s" % q
        data = backend.get_data(full_url)
        fake_qs = []
        for d in data:
            fake_qs.append(GeonameDict(d["id"], **d))
        return fake_qs
        

#    def get_result(self,obj):
#        log.debug(obj,"BBBBBB")
#        return unicode(obj)
        
    def format_match(self,obj):
        return obj["name"]
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
