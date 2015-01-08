from pyramid import testing

from whoahqa.tests import TestBase
from whoahqa.models import OnaUser
from whoahqa.security import group_finder


class TestGroupFinder(TestBase):
    def test_group_finder_returns_users_groups(self):
        self.setup_test_data()
        user = OnaUser.get(OnaUser.username == 'super').user

        request = testing.DummyRequest()
        groups = group_finder(user.id, request)
        self.assertListEqual(sorted(groups), sorted(['su', 'u:1']))

    def test_group_finder_returns_none_if_user_doesnt_exist(self):
        request = testing.DummyRequest()
        groups = group_finder(1234, request)
        self.assertIsNone(groups)
