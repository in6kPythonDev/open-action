
from external_resource import utils
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

def proxy(request, backend_name, url):
    """Retrieve url from a specific external backend"""

    backend = utils.load_backend(backend_name)
    rv = backend.get_url(url, request)
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
