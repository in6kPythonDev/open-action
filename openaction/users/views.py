from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.views import login as django_auth_login

from users.models import UserProfile
from askbot.models.post import Post
from askbot.models.repute import Vote
from askbot.models.user import User as AskbotUser
import askbot.utils.decorators as askbot_decorators
from action.models import Action
from action import const as a_consts
from django.views.generic.edit import FormView
from users.forms import UserRegistrationForm

from lib import views_support

class UserDetailView(DetailView):
    """ Show the given User details """

    def get_object(self, queryset=None):

        # object lookup using username
        object = User.objects.get(username=self.kwargs['username'])

        return object

class UserProfileListView(ListView):
    """ Show a list of Users details with other information about users 
    last activities """

    model = UserProfile
    template_name = 'profiles/profile_list.html'
    context_object_name = 'user_profiles'

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(UserProfileListView, self).get_context_data(**kwargs)

        context.update({
            'top_voted_actions': ["TODO"][:5],
            'top_active_topics': ["TODO"][:5],
            'top_active_locations': ["TODO"][:5],
        })
        return context

class UserProfileDetailView(DetailView, views_support.LoginRequiredView):
    """ Show the User profile page.

    The page contains:

    * voted actions : the actions the user joined to
    * friends : the user friends into the site
    * followed organizations : the organizations followed by the user
    * represented organizations : the organizations represented by the user
    * activities : the registered activities of the user
    * number of unread notices : notices sent to the user that he has not 
    read yet
    * number of voted active actions : the number of the active actions the 
    user joined to
    * number of activists involved : number of users who joined an action and 
    for which he was the referral 
    * global impact factor : how many joinings have been done thanks to the user
    
    """

    model = UserProfile
    template_name = 'profiles/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):

        # object lookup using username
        object = UserProfile.objects.get(user__username=self.kwargs['username'])

        return object

    def get_context_data(self, **kwargs):

        context = super(UserProfileDetailView, self).get_context_data(**kwargs)
        user = self.get_object().user
       
        #note: typo from django-notification "recieved" :)
        num_of_notices_unread = user.recieved_notices.filter(unseen=True).count()

        context.update({
            'voted_actions' : user.actions,
            'friends' : user.friends,
            'followed_orgs' : user.followed_orgs,
            'represented_orgs' : user.represented_orgs,
            'activities' : user.activity_set.all(),
            'num_of_notices_unread' : num_of_notices_unread,
            'num_of_voted_actions_active' : len(user.actions.actives()),
            'num_of_involved_activists' : user.involved_users.count(),
            'global_impact_factor' : user.global_impact_factor,
        })
        #print("\nContext: %s" % context)

        return context

@csrf_protect
@never_cache
def registration(request, *args, **kw):

    form_class = UserRegistrationForm
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, "Ti sei registrato con successo. Conferma via mail")
            return HttpResponseRedirect(settings.LOGIN_URL)
    else:
        form = form_class()

    context = {
        'registration_form' : form,
    }

    return render_to_response(
        "users/register.html", context,
        context_instance=RequestContext(request)
    )

@never_cache
def login(request, *args, **kw):

    return django_auth_login(request, template_name="users/login.html", *args, **kw)
