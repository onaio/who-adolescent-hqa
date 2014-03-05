import urlparse

from webob.multidict import MultiDict
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid import testing

from whoahqa.views.auth import check_post_csrf
from whoahqa.tests import (settings, IntegrationTestBase, FunctionalTestBase,)


class TestCheckPostCSRF(IntegrationTestBase):
    @staticmethod
    def func(context, request):
            return Response("Valid")

    def test_get_request_runs_func(self):
        request = testing.DummyRequest()
        inner = check_post_csrf(self.func)
        response = inner(None, request)
        self.assertEqual(response.status_code, 200)

    def test_post_with_valid_csrf_runs_func(self):
        request = testing.DummyRequest()
        payload = MultiDict([
            ('key', 'value'),
            ('csrf_token', request.session.get_csrf_token())
        ])
        request.method = "POST"
        request.POST = payload
        inner = check_post_csrf(self.func)
        response = inner(None, request)
        self.assertEqual(response.status_code, 200)

    def test_post_with_bad_csrf_fails(self):
        payload = MultiDict([
            ('key', 'value'),
            ('csrf_token', 'invalid')
        ])
        request = testing.DummyRequest(post=payload)
        inner = check_post_csrf(self.func)
        result = inner(None, request)
        self.assertIsInstance(result, HTTPBadRequest)

    def test_post_without_csrf_fails(self):
        payload = MultiDict([
            ('key', 'value'),
        ])
        request = testing.DummyRequest(post=payload)
        inner = check_post_csrf(self.func)
        result = inner(None, request)
        self.assertIsInstance(result, HTTPBadRequest)
