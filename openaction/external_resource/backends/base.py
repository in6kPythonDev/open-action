
import simplejson, urllib2

class ExternalResourceInfo(object):

    RESOURCE_TYPE_METHOD_MAP = None #To be defined in subclass

    def __init__(self, resource):
        self.resource = resource
        super(ExternalResourceInfo, self).__init__()


    def get_external_info(self):
        """Dispatcher to real getter method for specific resource type.

        Default machinery calls get_<resource_type>_info method
        """

        try:
            method_name = "get_%s_info" % self.resource.resource_type
        except KeyError as e:
            raise NotImplementedError(
                "Backend %s method to retrieve external info for a %s" % (
                self.__class__.__name__, self.resource.resource_type
            ))
        return getattr(self, method_name)()


#--------------------------------------------------------------------------------

class FBExternalResourceInfo(ExternalResourceInfo):

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

    def get_user_info(self):
        """Call Facebook API and return normalized data."""

        fields = ['id','name','email', 'username']
        auth_qs = self.get_auth_querystring()

        graphapi_url = "https://graph.facebook.com/%s?fields=%s&format=json&%s" % (self.id, ",".join(fields), auth_qs)

        raw_data = self.do_request(graphapi_url)
        data = simplejson.load(raw_data)
        
        normalized_data = {
            'id' : data.get('id'),
            'name' : data.get('name'),
            'email' : data.get('email'),
            'username' : data.get('username'),
        }

        return normalized_data

#--------------------------------------------------------------------------------

class OpenPolisExternalResourceInfo(ExternalResourceInfo):


    def get_auth_querystring(self):
        # Use OpenAction access token to build querystring (see: social auth)
        return "TODO"

    def get_politician_info(self):
        """Call OpenPolis API and return normalized data.

        TODO
        """

        fields = ['id','name','email', 'username']
        auth_qs = self.get_auth_querystring()

        graphapi_url = "https://graph.facebook.com/%s?fields=%s&format=json&%s" % (self.id, ",".join(fields), auth_qs)

        response = urllib2.open(graphapi_url)
        data = simplejson.load(response.read())
        
        normalize_data = {
            'id' : data.get('id'),
            'name' : data.get('name'),
            'email' : data.get('email'),
            'username' : data.get('username'),
        }

        return normalize_data
