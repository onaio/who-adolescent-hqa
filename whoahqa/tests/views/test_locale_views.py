from pyramid import testing
from webob.multidict import MultiDict

from whoahqa.tests.test_base import IntegrationTestBase, FunctionalTestBase
from whoahqa.views import set_locale

from whoahqa.models import OnaUser


class TestLocale(IntegrationTestBase):
    def setUp(self):
        super(TestLocale, self).setUp()
        self.setup_test_data()
        self.request = testing.DummyRequest()
        self.request.ona_user = OnaUser.get(OnaUser.username == "super")

    def test_locale_settings(self):
        params = MultiDict({'locale': 'pt'})
        self.request.method = 'POST'
        self.request.POST = params

        results = set_locale(self.request)
        user_setting = results['user_settings']
        self.assertEqual(user_setting.language, 'pt')


class TestLocaleFunctional(FunctionalTestBase):
    def test_new_locale_added_to_request(self):
        self.setup_test_data()
        url = self.request.route_url("locale", traverse=())
        headers = self._login_user('super')

        params = MultiDict({'locale': 'pt'})
        response = self.testapp.post(url, params, headers=headers)
        self.assertEqual(response.status_code, 200)
        header_values = str(response.headers.values())
        self.assertTrue("_LOCALE_=pt" in header_values)


# Test Actual cookie setting using functional test
