from django.views.generic import TemplateView
from action.models import Action

class HomepageView(TemplateView):

    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super(HomepageView,self).get_context_data(**kwargs)

        context['action_list'] = Action.objects.all()
        context['notifications'] = []

        return context