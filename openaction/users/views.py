from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.views.generic import DetailView
from django.views.generic.list import ListView

from users.models import UserProfile

class UserDetailView(DetailView):

    def get_object(self, queryset=None):

        # object lookup using username
        object = User.objects.get(username=self.kwargs['username'])

        return object

class UserProfileDetailView(DetailView):
    model = UserProfile
    template_name = 'profiles/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):

        # object lookup using username
        object = UserProfile.objects.get(user__username=self.kwargs['username'])

        return object

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(UserProfileDetailView, self).get_context_data(**kwargs)

        context['voted_actions'] = "TODO"
        context['friends'] = "TODO"
        context['followed_orgs'] = "TODO"
        context['represented_orgs'] = "TODO"

        return context


class UserProfileListView(ListView):
    model = UserProfile
    template_name = 'profiles/profile_list.html'

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(UserProfileListView, self).get_context_data(**kwargs)

        context.update({
            'top_voted_actions': ["TODO"][:5],
            'top_active_topics': ["TODO"][:5],
            'top_active_locations': ["TODO"][:5],
        })
        return context



