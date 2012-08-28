from django.views.generic.detail import DetailView

from action.models import Action

class ActionDetailView(DetailView):

    model = Action
    context_object_name="action" 
    template_name="action_detail.html"

    def get_object(self):
        self.instance = super(ActionDetailView, self).get_object()
        # needs to do something here...?
        # POSSIBLE TODO: parse token and increment counter "action suggested by user"
        return self.instance

    def get_context_data(self, **kwargs):

        context = super(ActionDetailView, self).get_context_data(**kwargs)
        # needs to do something here...?
        return context
