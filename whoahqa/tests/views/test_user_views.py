from httmock import urlmatch, HTTMock
from pyramid import testing

from whoahqa.models import (
    OnaUser,
    ReportingPeriod
)
from whoahqa.views import (
    UserViews,
)
from whoahqa.tests import (IntegrationTestBase, FunctionalTestBase,)


@urlmatch(netloc=r'(.*\.)?test.enketo\.org$', path='/api_v1/instance')
def get_edit_url_mock(url, request):  # pragma: no cover
    return {
        'status_code': 201,
        'content': '{"code": "201", "edit_url": "https://cz2pj-0.enketo.org/webform/edit?instance_id=2"}'  # noqa
    }


class TestUserViews(IntegrationTestBase):
    def setUp(self):
        super(TestUserViews, self).setUp()
        self.request = testing.DummyRequest()
        self.setup_test_data()
        self.user_views = UserViews(self.request)

    def test_user_clinics_view(self):
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        self.request.context = ona_user.user
        self.request.user = ona_user.user

        response = self.user_views.clinics()

        # we should only have Clinic A in the response
        self.assertIsInstance(response['period'], ReportingPeriod)
        self.assertEqual(len(response['locations']), 1)
        self.assertEqual(response['locations'][0].name, "Clinic A")

    def select_reporting_period(self):
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        request = testing.DummyRequest()
        request.context = ona_user.user
        request.user = ona_user.user
        user_views = UserViews(request)

        with HTTMock(get_edit_url_mock):
            response = user_views.select_reporting_period()

        self.assertGreater(len(response['periods']), 0)
        self.assertEquals(response['user'], ona_user.user)


class TestUserViewsFunctional(FunctionalTestBase):
    def test_user_clinics_view_allows_owner(self):
        self.setup_test_data()
        # get the manager user
        user = OnaUser.get(OnaUser.username == "manager_a").user
        url = self.request.route_path(
            'users', traverse=(user.id, 'clinics'))
        headers = self._login_user('manager_a')
        with HTTMock(get_edit_url_mock):
            response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_user_clinics_view_allows_super_user(self):
        self.setup_test_data()
        headers = self._login_user('super')
        # get the manager user
        user = OnaUser.get(OnaUser.username == "manager_a").user
        url = self.request.route_path(
            'users', traverse=(user.id, 'clinics'))
        with HTTMock(get_edit_url_mock):
            response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
