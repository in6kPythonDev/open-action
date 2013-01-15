from action.models import Geoname, ActionCategory
from django.conf import settings
from external_resource.utils import load_backend
from users.forms import UserRegistrationForm

def global_context(request):
    context = {}
    context['main_arguments'] = ActionCategory.objects.all()
    be = load_backend('locations')
    context['main_locations'] = sorted(be.get_data(be.base_url + 'locations/?location_type=regione', as_string=False), key=lambda x: x['name'])
    context['LESS_DEBUG'] = settings.LESS_DEBUG
    context['LOGIN_URL'] = settings.LOGIN_URL
    context['LOGOUT_URL'] = settings.LOGOUT_URL

    if not request.user.is_authenticated():
        context['registration_form'] = UserRegistrationForm()

    return context