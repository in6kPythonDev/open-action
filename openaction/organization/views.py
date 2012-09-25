from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.utils.decorators import method_decorator

import askbot.utils.decorators as askbot_decorators
from organization.models import UserOrgMap, Organization
from organization import exceptions as exceptions

from lib import views_support

class OrgView(DetailView, views_support.LoginRequiredView):
    """ Organization details view """

    model = Organization

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

        mapping, created = UserOrgMap.objects.get_or_create(user=user,
            org=org,
        )
        if mapping.is_follower:
            #DONE: Matteo raise appropriate exception
            raise exceptions.UserCannotFollowOrgTwice(user, org) 
        else:
            mapping.is_follower=True
            mapping.save()

        # QUESTION: should we notify (here or in an UserOrgMap post_save
        # signal) to the Organization that a new User is following them ?
        
        return views_support.response_success(request)
 
class UserRepresentOrgView(UserOrgMapView):
    """ Map a User to an Organization, defining the User as a representative 
    of the latter. """

    def post(self, request, *args, **kwargs):
        org = self.get_object()
        user = request.user

        mapping, created = UserOrgMap.objects.get_or_create(user=user,
            org=org,
        )
        if mapping.is_representative:
            #DONE: Matteo raise appropriate exception
            raise exceptions.UserCannotRepresentOrgTwice(user, org) 
        else:
            mapping.is_representative=True
            mapping.save()

        # QUESTION: should we notify (here or in an UserOrgMap post_save
        # signal) to the Organization that a new User is following them ?
        
        return views_support.response_success(request)
