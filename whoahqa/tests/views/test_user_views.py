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
        self.user_views = UserViews(self.request)

    def test_user_clinics_view(self):
        self.setup_test_data()
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        period.__parent__ = ona_user.user
        self.request.context = period
        self.request.ona_user = ona_user

        response = self.user_views.clinics()

        # we should only have Clinic A in the response
        self.assertIsInstance(response['period'], ReportingPeriod)
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic A")
        self.assertIn('key_indicators', response)
        self.assertIn('key_indicator_char_map', response)

    def test_user_summary_view(self):
        self.setup_test_data()
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        request = testing.DummyRequest()
        request.context = ona_user.user
        request.ona_user = ona_user
        user_views = UserViews(request)

        with HTTMock(get_edit_url_mock):
            response = user_views.clinics_score_summary()

        # we should only have Clinic A in the response
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic A")
        self.assertIn('characteristics', response)
        self.assertIn('clinic_scores', response)

    def select_reporting_period(self):
        self.setup_test_data()
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        request = testing.DummyRequest()
        request.context = ona_user.user
        request.ona_user = ona_user
        user_views = UserViews(request)

        with HTTMock(get_edit_url_mock):
            response = user_views.select_reporting_period()

        self.assertGreater(len(response['periods']), 0)
        self.assertEquals(response['user'], ona_user.user)

    def test_reporting_period_redirect(self):
        self.setup_test_data()
        user = OnaUser.get(OnaUser.username == 'manager_a').user
        self.request.context = user
        response = self.user_views.reporting_period_redirect()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, self.request.route_url(
            'users', traverse=(user.id, 'select-period'), _query={
                'came_from': self.request.route_path(
                    'users', traverse=(user.id, '{period_id}', 'clinics'))
            }))


class TestUserViewsFunctional(FunctionalTestBase):
    def test_user_clinics_view_allows_owner(self):
        self.setup_test_data()
        # get the manager user
        user = OnaUser.get(OnaUser.username == "manager_a").user
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        url = self.request.route_path(
            'users', traverse=(user.id, period.id, 'clinics'))
        headers = self._login_user('manager_a')
        with HTTMock(get_edit_url_mock):
            response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_user_clinics_view_allows_super_user(self):
        self.setup_test_data()
        headers = self._login_user('super')
        # get the manager user
        user = OnaUser.get(OnaUser.username == "manager_a").user
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        url = self.request.route_path(
            'users', traverse=(user.id, period.id, 'clinics'))
        with HTTMock(get_edit_url_mock):
            response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
