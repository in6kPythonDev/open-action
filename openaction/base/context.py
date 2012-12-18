from action.models import Geoname, ActionCategory
from django.conf import settings

def global_context(request):
    context = {}
    context['main_arguments'] = ActionCategory.objects.all()
    context['main_locations'] = Geoname.objects.all()
    context['LESS_DEBUG'] = settings.LESS_DEBUG

    return context