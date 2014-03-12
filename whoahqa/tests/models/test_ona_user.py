from whoahqa.models import (
    User,
    OnaUser,
)
from whoahqa.tests import TestBase


class TestOnaUser(TestBase):
    def test_get_or_create_from_api_data_creates_user(self):
        user_data = [{
            'username': u"user_one",
            'first_name': u"",
            'last_name': u""
        }]
        refresh_token = 'a123f4'
        ona_user = OnaUser.get_or_create_from_api_data(
            user_data,
            refresh_token)
        self.assertIsInstance(ona_user, OnaUser)
        self.assertIsInstance(ona_user.user, User)

    def test_get_or_create_from_api_data_returns_user_if_exists(self):
        user_data = [{
            'username': u"user_one",
            'first_name': u"",
            'last_name': u""
        }]
        # create the instance
        refresh_token = 'a123f4'
        OnaUser.get_or_create_from_api_data(user_data, refresh_token)

        # try to get or create
        new_refresh_token = 'b234f5'
        ona_user = OnaUser.get_or_create_from_api_data(
            user_data,
            new_refresh_token)
        self.assertIsInstance(ona_user, OnaUser)
        self.assertIsInstance(ona_user.user, User)
        self.assertEqual(ona_user.refresh_token, new_refresh_token)

    def test_get_or_create_from_api_data_raises_value_error_if_bad_user_len(
            self):
        user_data = [
            {
                'username': u"user_one",
                'first_name': u"",
                'last_name': u""
            }, {
                'username': u"user_one",
                'first_name': u"",
                'last_name': u""
            }]
        refresh_token = 'a123f4'
        self.assertRaises(
            ValueError,
            OnaUser.get_or_create_from_api_data,
            user_data,
            refresh_token)

    def test_get_or_create_from_api_data_raises_value_error_if_no_username(
            self):
        user_data = [
            {
                'first_name': u"",
                'last_name': u""
            }]
        refresh_token = 'a123f4'
        self.assertRaises(
            ValueError,
            OnaUser.get_or_create_from_api_data,
            user_data,
            refresh_token)

    def test_get_or_create_from_api_data_raises_value_error_if_blank_username(
            self):
        user_data = [
            {
                'username': u"",
                'first_name': u"",
                'last_name': u""
            }]
        refresh_token = 'a123f4'
        self.assertRaises(
            ValueError,
            OnaUser.get_or_create_from_api_data,
            user_data,
            refresh_token)
