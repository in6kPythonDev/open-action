from action.tests import OpenActionViewTestCase

import datetime

class UserOrgMapTest(OpenActionViewTestCase):

    def setUp(self):
        super(UserOrgMapTest, self).setUp()

        self._external_resource = self._create_external_resource(backend_name,
            resource_id,
            resource_type,
            first_get_on,
            last_get_on
        )
        self._org = self._create_organization(name=name,
            external_resource=self._external_resource)

    def _create_external_resource(backend_name,
            resource_id,
            resource_type,
            first_get_on,
            last_get_on
        ):
        pass

    def _create_organization(name, external_resource):
        pass

    def _do_post_user_follow_org(self, org, ajax=False):#, **kwargs):

        response = self._post(
            reverse('org-user-follow', args=(org.pk,)),
            ajax#,
            #kwargs
        )
        return response

#--------------------------------------------------------------------------------

    def test_user_follow_org_view(self, user=None):

        logged_in = self._login(user)

        if logged_in:
            response = self._do_post_user_follow_org(self._org) 

            self._check_for_success_response(response)

            self.assertTrue([self._author, user][user] in self.org.followers)
