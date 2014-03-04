import urlparse

from webob.multidict import MultiDict
from pyramid import testing
from httmock import urlmatch, HTTMock
from pyramid.httpexceptions import HTTPFound

from whoahqa.models import OnaUser
from whoahqa.views import (
    oauth_authorize,
    oauth_callback,
)
from whoahqa.views.auth import logout
from whoahqa.models import (
    Clinic,
)
from whoahqa.tests import (settings, IntegrationTestBase, FunctionalTestBase,)


class TestAuth(IntegrationTestBase):
    def test_oauth_authorize(self):
        request = testing.DummyRequest()
        response = oauth_authorize(request)

        # redirect url
        self.assertEqual(response.status_code, 302)

        # parse the url
        parse_result = urlparse.urlparse(response.headers['Location'])
        # url must equal oauth_authorization_endpoint
        base_url = "{scheme}://{netloc}{path}".format(
            scheme=parse_result.scheme,
            netloc=parse_result.netloc,
            path=parse_result.path)
        oauth_authorization_endpoint = "{base_url}{path}".format(
            base_url=settings['oauth_base_url'],
            path=settings['oauth_authorization_path'])
        self.assertEqual(base_url, oauth_authorization_endpoint)

        # query params must include 1. correct client_id 2. required scopes
        # and 3. correct redirect url
        query_params = dict(urlparse.parse_qsl(parse_result.query))
        self.assertEqual(
            query_params['client_id'],
            settings['oauth_client_id'])
        self.assertEqual(query_params['scope'].split(),
                         ['read', 'groups'])
        self.assertEqual(
            query_params['redirect_uri'],
            request.route_url('auth', action="callback"))

        # test that the `oauth_state` is saved in the session
        self.assertIn('oauth_state', request.session)

    def test_oauth_authorize_accepted(self):
        pass

    def test_oauth_authorize_canceled(self):
        request = testing.DummyRequest()
        request.GET = MultiDict([
            ('error', u"access_denied"), ('state', 'a123f4')])
        response = oauth_callback(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers['Location'],
            request.route_url('auth', action='login'))

    def test_logout(self):
        request = testing.DummyRequest()
        response = logout(request)
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(
            response.location, request.route_url('auth', action='login'))


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


class TestAuthFunctional(FunctionalTestBase):
    @staticmethod
    @urlmatch(netloc='accounts.example.com', path='/o/token')
    def oauth_token_mock(url, request):
        return {
            'status_code': 200,
            'content': '{"access_token":"1/fFAGRNJru1FTz70BzhT3Zg", "expires_in":3920, "token_type":"Bearer", "refresh_token":"1/f4YTbBjMoBbXfg7oFh_FKg6r3r6bh8M9Y-0"}'
        }

    @staticmethod
    @urlmatch(netloc='accounts.example.com', path='/api/v1/users')
    def oauth_users_mock(url, request):
        return {
            'status_code': 200,
            'content': '[{"username": "user_one", "first_name": "", "last_name": ""}]'
        }

    def test_oauth_login_response(self):
        url = self.request.route_url('auth', action='login')
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_oauth_authorize_accepted(self):
        state = 'a123f4'
        code = 'f27299'
        url = self.request.route_path('auth', action='callback')
        with HTTMock(TestAuthFunctional.oauth_token_mock,
                     TestAuthFunctional.oauth_users_mock):
            response = self.testapp.get(url, params={
                'state': state,
                'code': code
            })

        # test that user is gotten or created
        ona_user = OnaUser.get(OnaUser.username == 'user_one')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            self.request.route_url(
                'users', traverse=(ona_user.user.id, 'clinics')))

        # check that we set the login header
        self.assertIn('Set-Cookie', response.headers)

