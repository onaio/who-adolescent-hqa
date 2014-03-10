from whoahqa.tests.test_base import FunctionalTestBase


class TestReportingPeriodsFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestReportingPeriodsFunctional, self).setUp()
        self.setup_test_data()

    def test_list_allows_su(self):
        headers = self._login_user('super')
        url = self.request.route_path('periods', traverse=())
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_list_denies_non_su(self):
        headers = self._login_user('manager_a')
        url = self.request.route_path('periods', traverse=())
        response = self.testapp.get(url, headers=headers, status=403)
        self.assertEqual(response.status_code, 403)
