from django.core.urlresolvers import reverse

from action.tests import OpenActionViewTestCase
from action_request.models import ActionRequest 

import datetime

class ActionRequestModerationTest(OpenActionViewTestCase):

    def setUp(self):
        super(ActionRequestModerationTest, self).setUp()

 
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

    def _do_POST_create_action_moderation_request(self, org, ajax=False):

        response = self._POST(
            reverse('action-moderation-request', args=(org.pk,)),
            ajax
        )
        return response

#--------------------------------------------------------------------------------

    def test_create_action_moderation_request(self, user=None):
        pass
