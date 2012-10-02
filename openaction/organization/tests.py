from django.core.urlresolvers import reverse

from action.tests import OpenActionViewTestCase
from organization.models import UserOrgMap #Organization, 

import datetime

class UserOrgMapTest(OpenActionViewTestCase):

    def setUp(self):
        super(UserOrgMapTest, self).setUp()

        #self._external_resource = self._create_external_resource(backend_name,
        #    resource_id,
        #    resource_type,
        #    first_get_on,
        #    last_get_on
        #)

        org_name = "Organization 1"
        self._org = self._create_organization(name=org_name)

    def _create_external_resource(self,
            backend_name,
            resource_id,
            resource_type,
            first_get_on,
            last_get_on
        ):
        pass

    def _POST(self, url, is_ajax, **kwargs):
        
        if is_ajax:
            response = self._c.post(url,
                kwargs,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
        else:
            response = self._c.post(url,
                kwargs
            )
        return response

    def _do_POST_user_follow_org(self, org, ajax=False):

        response = self._POST(
            reverse('org-user-follow', args=(org.pk,)),
            ajax
        )
        return response
    
    def _do_POST_user_represent_org(self, org, user=None, ajax=False):

        #KO:it shouldn't be possible to do this through POST
        #response = self._POST(
        #    reverse('org-user-represent', args=(org.pk,)),
        #    ajax
        #)
        #return response

        #HACK
        org = org
        user = [self._author, user][bool(user)]

        mapping, created = UserOrgMap.objects.get_or_create(user=user,
            org=org,
            is_representative=True
        )
        return


#--------------------------------------------------------------------------------

#    def test_org_view

    def test_user_follow_org_view(self, user=None):

        logged_in = self._login(user)

        if logged_in:
            response = self._do_POST_user_follow_org(self._org,
                ajax=True
            )

            if user:
                _user = user
            else:
                _user = self._author

            self._check_for_success_response(response)

            try:
                usrorgmap_obj = UserOrgMap.objects.get(user=_user)
            except UserOrgMap.DoesNotExist as e:
                usrorgmap_obj = False

            self.assertTrue(usrorgmap_obj)

            self.assertTrue(_user in self._org.followers)
            self.assertTrue(self._org in _user.followed_orgs)

    def test_user_represent_org_view(self, user=None):
        """ This test has to be rebuild, now it uses ah hack in the 
        POST method to manually create a mapping between org and
        user --> POST method is not allowed for doing this
        """

        logged_in = self._login(user)

        if logged_in:
            response = self._do_POST_user_represent_org(self._org,
                user,
                ajax=True
            )

            if user:
                _user = user
            else:
                _user = self._author

            #self._check_for_success_response(response)

            try:
                usrorgmap_obj = UserOrgMap.objects.get(user=_user)
            except UserOrgMap.DoesNotExist as e:
                usrorgmap_obj = False

            self.assertTrue(usrorgmap_obj)

            self.assertTrue(_user in self._org.representatives)
            self.assertTrue(self._org in _user.represented_orgs)
