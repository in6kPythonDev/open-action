
from external_resource import utils

def proxy(request, backend_name, url):
    """Retrieve url from a specific external backend"""

    backend = utils.load_backend(backend_name)
    rv = backend.get_url(url)
    return rv
