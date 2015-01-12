from pyramid import testing
from webob.multidict import MultiDict

from whoahqa.constants import groups
from whoahqa.models import OnaUser
from whoahqa.tests import IntegrationTestBase, FunctionalTestBase
from whoahqa.views.admin import AdminViews


class TestAdminViews(IntegrationTestBase):
    def setUp(self):
        super(TestAdminViews, self).setUp()
        self.setup_test_data()
        self.request = testing.DummyRequest()
        self.view = AdminViews(self.request)

    def test_can_edit_user_groups(self):
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        user = ona_user.user
        self.request.context = user

        self.request.method = 'POST'
        params = MultiDict({'group': groups.CLINIC_MANAGER})
        self.request.POST = params

        response = self.view.edit()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(ona_user.user.group.name,
                         groups.CLINIC_MANAGER)


class TestAdminViewsFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestAdminViewsFunctional, self).setUp()
        self.setup_test_data()

    def test_only_super_user_can_list_user_roles(self):
        url = self.request.route_url(
            'admin', traverse=())
        headers = self._login_user('manager_b')
        response = self.testapp.get(url, headers=headers, status=403)
        # Clinic Manager cannot access Admin pages
        self.assertEqual(response.status_code, 403)

        # Super User can access admin view
        headers = self._login_user('super')
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_only_super_user_can_change_user_roles(self):
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        url = self.request.route_url(
            'admin', traverse=(ona_user.user.id, 'edit'))

        headers = self._login_user('manager_b')
        response = self.testapp.get(url, headers=headers, status=403)
        # Clinic Manager cannot access Admin pages
        self.assertEqual(response.status_code, 403)

        # Super User can access admin view
        headers = self._login_user('super')
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
