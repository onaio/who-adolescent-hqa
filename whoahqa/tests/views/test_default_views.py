from whoahqa.constants import groups
from whoahqa.tests import FunctionalTestBase
from whoahqa.models import User
from whoahqa.views.helpers import get_period_from_request


class TestDefaultViewsFunctional(FunctionalTestBase):
    def test_redirects_to_clinics_when_authenticated(self):
        self.setup_test_data()
        url = self.request.route_url('default')
        headers = self._login_user("manager_b")
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 302)

    def test_redirects_to_states_for_national_official(self):
        self.setup_test_data()
        self._create_dash_user(
            "national", "national", "national@email.com",
            groups.NATIONAL_OFFICIAL)
        user = User.newest()

        url = self.request.route_url('default')
        headers = self._login_dashboard_user(user)
        response = self.testapp.get(url, headers=headers)

        period = get_period_from_request(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.request.route_url(
                'states', traverse=(),
                _query={'period': period.id}),
            response.location)
