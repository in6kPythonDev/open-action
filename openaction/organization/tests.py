from unittest import TestCase

from connection import *

class UserOrganizationMappingTest(TestCase):

    def setUp(self):

        self._create_organization(name=name,
            external_resource=external_resource)
        
