from whoahqa.tests import FunctionalTestBase


class TestDefaultViewsFunctional(FunctionalTestBase):
    def test_redirects_to_clinics_when_authenticated(self):
        self.setup_test_data()
        url = self.request.route_url('default')
        headers = self._login_user("manager_a")
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            self.request.route_url('clinics', traverse=()))
