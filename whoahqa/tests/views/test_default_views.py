from whoahqa.tests import FunctionalTestBase
from whoahqa.models import (
    Clinic,
)


class TestDefaultViewsFunctional(FunctionalTestBase):
    def test_redirects_to_clinics_when_authenticated(self):
        self.setup_test_data()
        url = self.request.route_url('default')
        headers = self._login_user("manager_a")
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers['Location'],
            self.request.route_url('clinics', traverse=()))


class TestForbiddenViewFunctional(FunctionalTestBase):
    def test_render_login_when_forbidden_and_not_authenticated(self):
        url = self.request.route_url('default')
        response = self.testapp.get(url, status=401)
        self.assertEqual(response.status_code, 401)
        response.mustcontain('<title>Login')

    def test_render_unauthorized_when_forbidden_and_authenticated(self):
        # TODO: move setup_test_data call to setUp
        self.setup_test_data()
        clinic = Clinic.get(Clinic.name == "Clinic A")
        url = self.request.route_url('clinics', traverse=(clinic.id,))
        headers = self._login_user('manager_b')
        response = self.testapp.get(url, headers=headers, status=403)
        self.assertEqual(response.status_code, 403)
