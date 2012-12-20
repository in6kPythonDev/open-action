from action.models import Geoname, ActionCategory
from django.conf import settings
from users.forms import UserRegistrationForm

def global_context(request):
    context = {}
    context['main_arguments'] = ActionCategory.objects.all()
    context['main_locations'] = Geoname.objects.all()
    context['LESS_DEBUG'] = settings.LESS_DEBUG
    context['LOGIN_URL'] = settings.LOGIN_URL
    context['LOGOUT_URL'] = settings.LOGOUT_URL

    if not request.user.is_authenticated():
        context['registration_form'] = UserRegistrationForm()

    return context