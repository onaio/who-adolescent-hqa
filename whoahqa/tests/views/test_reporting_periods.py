import deform

from pyramid import testing
from webob.multidict import MultiDict

from whoahqa.views.reporting_periods import ReportingPeriodViews
from whoahqa.tests.test_base import IntegrationTestBase, FunctionalTestBase


class TestReportingPeriods(IntegrationTestBase):
    def setUp(self):
        super(TestReportingPeriods, self).setUp()
        self.request = testing.DummyRequest()
        self.view = ReportingPeriodViews(self.request)

    def test_create_POST_creates_period(self):
        self.request.method = "POST"
        self.request.POST = MultiDict([
            ('title', "2013/2014"),
            ('start_date', '1-02-2014'),
            ('end_date', '1-01-2015')
        ])
        response = self.view.create()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            self.request.route_url('periods', traverse=('list')))

    def test_create_invalid_POST_response(self):
        self.request.method = "POST"
        self.request.POST = MultiDict([
            ('title', "2013/2014"),
            ('start_date', '02-2014'),
            ('end_date', '02-2014'),
        ])
        response = self.view.create()
        self.assertIn('form', response)

    def test_create_GET_response(self):
        response = self.view.create()
        self.assertIn('form', response)
        self.assertIsInstance(response['form'], deform.Form)


class TestReportingPeriodsFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestReportingPeriodsFunctional, self).setUp()
        self.setup_test_data()
        self._create_user('john')

    def test_list_allows_su(self):
        headers = self._login_user('super')
        url = self.request.route_path('periods', traverse=('list'))
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_create_denies_non_su(self):
        headers = self._login_user('john')
        url = self.request.route_path('periods', traverse=('new'))
        response = self.testapp.get(url, headers=headers, status=403)
        self.assertEqual(response.status_code, 403)

    # TODO: test permissions on create view
