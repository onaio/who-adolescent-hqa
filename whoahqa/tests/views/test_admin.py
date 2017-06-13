from pyramid import testing
from webob.multidict import MultiDict

from whoahqa.constants import groups
from whoahqa.models import Municipality, OnaUser, State, User, UserProfile
from whoahqa.tests import IntegrationTestBase, FunctionalTestBase
from whoahqa.views.admin import AdminViews
from sqlalchemy.orm.exc import NoResultFound


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
        params = MultiDict({'group': groups.CLINIC_MANAGER,
                            'clinics': ['1'],
                            'municipality': '1',
                            'state': '2'})
        self.request.POST = params

        response = self.view.edit()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(ona_user.user.group.name,
                         groups.CLINIC_MANAGER)

    def test_can_register_new_clinic_users(self):
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        user = ona_user.user
        old_user_count = User.count()
        self.request.context = user

        self.request.method = 'POST'
        params = MultiDict({'email': "test@email.com",
                            'username': "test_user",
                            'password': {'password': 'password',
                                         'password-confirm': 'password'},
                            'group': groups.CLINIC_MANAGER,
                            'clinics': ['1']})
        self.request.POST = params

        response = self.view.register()
        self.assertEqual(User.count(), old_user_count + 1)
        self.assertEqual(response.status_code, 302)

    def test_can_register_new_municipality_users(self):
        self._create_municipality()
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        user = ona_user.user
        old_user_count = User.count()
        municipality = Municipality.newest()
        self.request.context = user

        self.request.method = 'POST'
        params = MultiDict({'email': "test@email.com",
                            'username': "test_user",
                            'password': {'password': 'password',
                                         'password-confirm': 'password'},
                            'group': groups.MUNICIPALITY_MANAGER,
                            'municipality': "{}".format(municipality.id)})
        self.request.POST = params

        response = self.view.register()
        self.assertEqual(User.count(), old_user_count + 1)
        self.assertEqual(response.status_code, 302)

    def test_can_register_new_state_users(self):
        self._create_state()
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        user = ona_user.user
        old_user_count = User.count()
        state = State.newest()
        self.request.context = user

        self.request.method = 'POST'
        params = MultiDict({'email': "test@email.com",
                            'username': "test_user",
                            'password': {'password': 'password',
                                         'password-confirm': 'password'},
                            'group': groups.STATE_OFFICIAL,
                            'state': "{}".format(state.id)})
        self.request.POST = params

        response = self.view.register()
        self.assertEqual(User.count(), old_user_count + 1)
        self.assertEqual(response.status_code, 302)

    def test_can_delete_ona_user(self):
        self._create_user("to_delete")
        ona_user_to_delete = OnaUser.get(OnaUser.username == 'to_delete')
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        self.request.method = 'GET'
        self.request.user = ona_user.user
        self.request.context = ona_user_to_delete

        response = self.view.delete()

        self.assertEqual(response.status_code, 302)
        self.assertRaises(
            NoResultFound,
            OnaUser.get, OnaUser.user_id == ona_user_to_delete.user_id)

    def test_can_delete_dashboard_user(self):
        self._create_dash_user('dash_user', '1234', 'test@me.com')
        dashboard_user = UserProfile.get(UserProfile.username == 'dash_user')
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        self.request.method = 'GET'
        self.request.user = ona_user.user
        self.request.context = dashboard_user

        response = self.view.delete()

        self.assertEqual(response.status_code, 302)
        self.assertRaises(
            NoResultFound,
            UserProfile.get,
            OnaUser.user_id == dashboard_user.user_id)


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
