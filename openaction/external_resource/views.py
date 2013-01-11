
from external_resource import utils
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

def proxy(request, backend_name, url):
    """Retrieve url from a specific external backend"""
    backend = utils.load_backend(backend_name)
    rv = backend.get_url(url, request)
    if '"exception": "location could not be found. OpLocation matching query does not exist."' in rv.content:

        from external_resource.backends.openpolis import OpenPolisLocationsBackend
        from django.http import HttpResponse
        import json

        locations = OpenPolisLocationsBackend(backend.settings_dict)

        loc_url = backend.base_url + 'locations/'
        loc = locations.get_data(loc_url+url)

        first_city, data = None, {}
        if loc['location_type']['name'] == 'Regione':
            first_city = backend.get_data('%s?location_type=comune&regional_id=%s&limit=1'% (loc_url,loc['regional_id']))[0]
            data = backend.get_data(backend.base_url+'cityreps/op_id/%s' % first_city['id'] )
            data['city_representatives']['provincia'] = {'giunta':[],'consiglio':[]}
        elif loc['location_type']['name'] == 'Provincia':
            first_city = backend.get_data('%s?location_type=comune&provincial_id=%s&limit=1'% (loc_url,loc['provincial_id']))[0]
            data = backend.get_data(backend.base_url+'cityreps/op_id/%s' % first_city['id'] )
            data['city_representatives']['regione'] = {'giunta':[],'consiglio':[]}

        data['city_representatives']['comune'] = {'giunta':[],'consiglio':[]}
        data['city_representatives']['camera'] = {'representatives':[]}
        data['city_representatives']['senato'] = {'representatives':[]}
        data['city_representatives']['europarl'] = {'representatives':[]}
        data['city_representatives']['location'] = ''

        rv = HttpResponse(json.dumps(data), mimetype='application/json')

    return rv

@method_decorator(login_required)
def cityreps_proxy(request, url):
    """Retrieve url from cityreps backend"""

    backend_name = "cityreps"
    backend = utils.load_backend(backend_name)
    rv = backend.get_url(url, request)
    # NOTE: default implementation of get_url already has 
    # mimetype as "application/json"
    return rv
