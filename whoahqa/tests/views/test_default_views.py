from whoahqa.models import OnaUser
from whoahqa.tests import FunctionalTestBase


class TestDefaultViewsFunctional(FunctionalTestBase):
    def test_redirects_to_clinics_when_authenticated(self):
        self.setup_test_data()
        url = self.request.route_url('default')
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        headers = self._login_user("manager_a")
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            self.request.route_url(
                'users',
                traverse=(ona_user.user.id, 'select-period'),
                _query={
                    'came_from': self.request.route_path(
                        'users', traverse=(
                            ona_user.user.id, '{period_id}', 'clinics'))}))
        response = response.follow(headers=headers)
        self.assertEqual(response.status_code, 200)
