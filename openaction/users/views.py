from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator

from users.models import UserProfile
from askbot.models.post import Post
from askbot.models.repute import Vote
from askbot.models.user import User as AskbotUser
import askbot.utils.decorators as askbot_decorators
from action.models import Action
from action import const as a_consts

from lib import views_support

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
    context_object_name = 'user_profile'

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(UserProfileListView, self).get_context_data(**kwargs)

        context.update({
            'top_voted_actions': ["TODO"][:5],
            'top_active_topics': ["TODO"][:5],
            'top_active_locations': ["TODO"][:5],
        })
        return context

class UserProfileView(DetailView, views_support.LoginRequiredView):

    model = UserProfile
    template_name = 'profiles/user_profile.html'

    def get_object(self, queryset=None):
        # object lookup using username
        profile = UserProfile.objects.get(user__username=self.kwargs['username'])
        return profile

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)

        #detVails
        user_profile = self.get_object()
        user = user_profile.user
       
        #lists 
        user_action_list = self.actions(user)
        user_friends_list = user.friends() 
        user_followed_organizations_list = user.orgmap_set.all() 

        #information
        user_activities = user.activity_set.all()
        user_notices_unread = user.recieved_notices.filter(unseen=True)
        user_active_actions_number = len(self.active_actions(
                user, user_action_list
            )
        )
        user_involved_activists = self.involved_actvists_number(user)


        context.update({
            'user_profile' : user_profile,
            'user' : user,
            'action_list' : user_action_list,
            'friends_list' : user_friends_list,
            'followed_organization' : user_followed_organizations_list,
            'activities' : user_activities,
            'unread_notices' : user_notices_unread,
            'number_of_active_actions' : user_active_actions_number,
            'number_of_involved_activists' : user_involved_activists,
        })

        return context

    #def active_actions(self, user):
    #    active_actions = [] 

    #    for action in Action.objects.all():
    #        if action.status in (a_consts.ACTION_STATUS_ACTIVE) and user.pk in action.voters:
    #            active_actions.append(action)

    #    return active_actions
       
    def actions(self, user):
        user_votes = user.votes.all()
        questions = Post.objects.filter(pk__in=user_votes)
        actions = Action.objects.filter(pk__in=questions)

        return actions

    def active_actions(self, user, actions):
        active_actions = [action for action in actions  if action.status in (
            a_consts.ACTION_STATUS_ACTIVE
        )]

        return active_actions
 
    def involved_actvists_number(self, user):
        return Vote.objects.filter(referral=user).count()
