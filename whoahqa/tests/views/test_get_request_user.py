from pyramid import testing

from whoahqa.models import (
    User,
)
from whoahqa.views import (
    get_request_user,
)
from whoahqa.tests import TestBase


class TestGetRequestUser(TestBase):
    def setUp(self):
        super(TestGetRequestUser, self).setUp()
        self.setup_test_data()
        self.request = testing.DummyRequest()

    def test_returns_user_if_authenticated(self):
        self.config.testing_securitypolicy(
            userid='1', permissive=True)
        user = get_request_user(self.request)
        self.assertIsInstance(user, User)

    def test_sets_none_if_id_not_authenticated(self):
        self.config.testing_securitypolicy(
            userid=None, permissive=False)
        user = get_request_user(self.request)
        self.assertIsNone(user)
