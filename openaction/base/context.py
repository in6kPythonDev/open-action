from action.models import Geoname, ActionCategory

def global_context(request):
    context = {}
    context['main_arguments'] = ActionCategory.objects.all()
    context['main_locations'] = Geoname.objects.all()

    return context