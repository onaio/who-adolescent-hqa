from pyramid import testing
from whoahqa.models import (
    OnaUser,
)
from whoahqa.views import (
    UserViews,
)
from whoahqa.tests import (IntegrationTestBase, FunctionalTestBase,)


class TestUserViews(IntegrationTestBase):
    def test_user_clinics_view(self):
        self.setup_test_data()
        user = OnaUser.get(OnaUser.username == 'manager_a').user
        request = testing.DummyRequest()
        request.context = user
        user_views = UserViews(request)
        response = user_views.clinics()

        # we should only have Clinic A in the response
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic A")


class TestUserViewsFunctional(FunctionalTestBase):
    def test_user_clinics_view_allows_owner(self):
        self.setup_test_data()
        # get the manager user
        user = OnaUser.get(OnaUser.username == "manager_a").user
        url = self.request.route_path('users', traverse=(user.id, 'clinics'))
        headers = self._login_user('manager_a')
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_user_clinics_view_allows_super_user(self):
        self.setup_test_data()
        headers = self._login_user('super')
        # get the manager user
        user = OnaUser.get(OnaUser.username == "manager_a").user
        url = self.request.route_path('users', traverse=(user.id, 'clinics'))
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)