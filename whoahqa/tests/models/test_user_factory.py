from pyramid import testing

from whoahqa.models import (
    UserFactory,
    User,
)
from whoahqa.tests import TestBase


class TestUserFactory(TestBase):
    def test_get_item_returns_user_if_id_exists(self):
        self.setup_test_data()
        user = User.newest()

        request = testing.DummyRequest()
        user = UserFactory(request).__getitem__(user.id)
        self.assertIsInstance(user, User)

    def test_get_item_raises_key_error_if_id_doesnt_exist(self):
        # invalid clinic id
        user_id = -1

        request = testing.DummyRequest()
        self.assertRaises(KeyError,
                          UserFactory(request).__getitem__, user_id)

    def test_get_item_raises_key_error_if_bad_int(self):
        # invalid clinic id
        user_id = "abc"

        request = testing.DummyRequest()
        self.assertRaises(KeyError,
                          UserFactory(request).__getitem__, user_id)
