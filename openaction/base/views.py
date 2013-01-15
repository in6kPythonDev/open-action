from django.views.generic import TemplateView
from action.models import Action, Politician
from askbot.models import Activity

class HomepageView(TemplateView):

    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super(HomepageView,self).get_context_data(**kwargs)

        context['action_list'] = Action.objects.all()[:5]
        context['latest_activities'] = Activity.objects.order_by('-active_at').all()[:5]
        context['politician_list'] = Politician.objects.all().order_by('?')[:5]


        return context