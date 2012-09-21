from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.utils.decorators import method_decorator

import askbot.utils.decorators as askbot_decorators
from organization.models import UserOrgMap, Organization

from lib import views_support

#class UserOrgMapView(FormView):
#    """ Generic view for the managememnt of the relationship among 
#    users and organizations """
#
#    form_class = UserOrgMap
#
#    @method_decorator(askbot_decorators.check_spam('text'))
#    def dispatch(self, request, *args, **kwargs):
#        return super(UserOrgMapView, self).dispatch(request, *args, **kwargs)
#
#    def get_form(self, form_class):
#        form = super(UserOrgMapView, self).get_form(form_class)
#        form.hide_field('user')
#        form.hide_field('is_representative')
#        form.hide_field('is_follower')
#
#        return form
#
#class UserFollowOrgView(UserOrgMapView, views_support.LoginRequiredView):
#    """ Map a User to an Organization, defining the User as a follower 
#    of the latter. """
#
#    def form_valid(self, form):
#
#        user = self.request.user
#        organization = form.cleaned_data['org']
#
#        mapping, created = UserOrgMap.objects.get_or_create(user=user,
#            org=organization,
#            is_follower=True
#        )
#
#        # QUESTION: should we notify (here or in an UserOrgMap post_save
#        # signal) to the Organization that a new User is following them ?
#
#        success_url = org.get_absolute_url()
#        return views_support.response_redirect(self.request, success_url)
 
class OrgView(DetailView, views_support.LoginRequiredView):
    """ Organization details view """

    model = Organization

    @method_decorator(askbot_decorators.check_spam('text'))
    def dispatch(self, request, *args, **kwargs):
        return super(ActionView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OrgView, self).get_context_data(kwargs)
        return context 

class UserOrgMapView(SingleObjectMixin, views_support.LoginRequiredView):
    """ Generic view for the managememnt of the relationship among 
    users and organizations """

    model = Organization

class UserFollowOrgView(UserOrgMapView):
    """ Map a User to an Organization, defining the User as a follower 
    of the latter. """

    def post(self, request, *args, **kwargs):
        org = self.get_object()
        user = request.user

        # QUESTION: should we perform some check or assert something
        # here? 

        mapping, created = UserOrgMap.objects.get_or_create(user=user,
            org=org,
            is_follower=True
        )

        # QUESTION: should we notify (here or in an UserOrgMap post_save
        # signal) to the Organization that a new User is following them ?
        
        return views_support.response_success(request)
 
