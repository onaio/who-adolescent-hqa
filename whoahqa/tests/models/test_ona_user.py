from whoahqa.models import (
    User,
    OnaUser,
    Municipality,
    State
)

from whoahqa.constants import groups

from whoahqa.tests import TestBase


class TestOnaUser(TestBase):
    def test_get_or_create_from_api_data_creates_user(self):
        user_data = {
            'username': u"user_one",
            'first_name': u"",
            'last_name': u""
        }
        refresh_token = 'a123f4'
        ona_user = OnaUser.get_or_create_from_api_data(
            user_data,
            refresh_token)
        self.assertIsInstance(ona_user, OnaUser)
        self.assertIsInstance(ona_user.user, User)

    def test_get_or_create_from_api_data_returns_user_if_exists(self):
        user_data = {
            'username': u"user_one",
            'first_name': u"",
            'last_name': u""
        }
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
        user_data = {
            'username': None,
            'first_name': u"",
            'last_name': u""}
        refresh_token = 'a123f4'
        self.assertRaises(
            ValueError,
            OnaUser.get_or_create_from_api_data,
            user_data,
            refresh_token)

    def test_get_or_create_from_api_data_raises_value_error_if_no_username(
            self):
        user_data = {
            'first_name': u"",
            'last_name': u""}
        refresh_token = 'a123f4'
        self.assertRaises(
            ValueError,
            OnaUser.get_or_create_from_api_data,
            user_data,
            refresh_token)

    def test_get_or_create_from_api_data_raises_value_error_if_blank_username(
            self):
        user_data = {
            'username': u"",
            'first_name': u"",
            'last_name': u""}
        refresh_token = 'a123f4'
        self.assertRaises(
            ValueError,
            OnaUser.get_or_create_from_api_data,
            user_data,
            refresh_token)

    def test_update_ona_user_location(self):
        self.setup_test_data()
        self._create_municipality('Brazlandia')
        municipality = Municipality.get(Municipality.name == 'Brazlandia')

        values = {'group': groups.MUNICIPALITY_MANAGER,
                  'municipality': municipality.id}

        manager = OnaUser.get(OnaUser.username == 'manager_a')

        manager.update(values)

        self.assertEqual(manager.location, municipality)

    def test_update_new_user_group(self):
        user = User()
        ona_user = OnaUser(
            user=user, username='user_a', refresh_token="c563e9")

        self._create_municipality('Brazlandia')
        municipality = Municipality.get(Municipality.name == 'Brazlandia')

        values = {'group': groups.MUNICIPALITY_MANAGER,
                  'municipality': municipality.id}

        ona_user.update(values)

        self.assertEqual(ona_user.group.name, groups.MUNICIPALITY_MANAGER)
        self.assertEqual(ona_user.location, municipality)

    def test_update_user_to_state_official(self):
        self.setup_test_data()
        self._create_state('Acre')
        state = State.get(Municipality.name == 'Acre')

        values = {'group': groups.STATE_OFFICIAL,
                  'state': state.id}

        manager = OnaUser.get(OnaUser.username == 'manager_a')

        manager.update(values)
        self.assertEqual(manager.location, state)

    def test_add_clinics_to_user(self):
        self.setup_test_data()
        user = User()
        ona_user = OnaUser(
            user=user, username='user_b', refresh_token="c563e9")

        values = {'group': groups.CLINIC_MANAGER,
                  'clinics': ["1", "2", "3"]}

        ona_user.update(values)

        self.assertEqual(len(ona_user.user.clinics), 3)
