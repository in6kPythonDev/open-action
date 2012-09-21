from django.core.urlresolvers import reverse

from action.tests import OpenActionViewTestCase
from organization.models import Organization, UserOrgMap

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

    def _create_organization(self, name, external_resource=None):
        org, created = Organization.objects.get_or_create(name=name)
        return org

    def _post(self, url, is_ajax, **kwargs):
        
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

    def _do_post_user_follow_org(self, org, ajax=False):#, **kwargs):

        response = self._post(
            reverse('org-user-follow', args=(org.pk,)),
            ajax#,
            #kwargs
        )
        return response

#--------------------------------------------------------------------------------

#    def test_org_view

    def test_user_follow_org_view(self, user=None):

        logged_in = self._login(user)

        if logged_in:
            response = self._do_post_user_follow_org(self._org,
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
