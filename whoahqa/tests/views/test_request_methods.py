from pyramid import testing

from whoahqa.constants import groups
from whoahqa.models import OnaUser
from whoahqa.tests import IntegrationTestBase

from whoahqa.views.request_methods import (
    can_list_clinics,
    can_view_clinics)


class TestRequestMethods(IntegrationTestBase):
    def setUp(self):
        super(TestRequestMethods, self).setUp()
        self.setup_test_data()
        self.request = testing.DummyRequest()
        self._create_user("john")

    def test_manager_can_list_clinics(self):
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        self.config.testing_securitypolicy(
            userid=ona_user.user.id,
            permissive=True,
            groupids=(groups.MUNICIPALITY_MANAGER,))
        has_permission = can_list_clinics(self.request)
        self.assertTrue(has_permission)

    def test_user_cannot_list_clinics(self):
        ona_user = OnaUser.get(OnaUser.username == 'john')
        self.config.testing_securitypolicy(
            permissive=False,
            userid=ona_user.user.id)
        has_permission = can_list_clinics(self.request)
        self.assertFalse(has_permission)

    def test_user_can_view_clinics(self):
        ona_user = OnaUser.get(OnaUser.username == 'john')
        self.config.testing_securitypolicy(
            permissive=True,
            userid=ona_user.user.id)
        has_permission = can_view_clinics(self.request)
        self.assertTrue(has_permission)
