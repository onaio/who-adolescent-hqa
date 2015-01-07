import transaction

from whoahqa.constants import characteristics as constants
from whoahqa.models import (
    DBSession,
    User,
    Clinic,
)
from whoahqa.tests import TestBase


class TestBaseModel(TestBase):
    def test_newest_returns_newest_record_by_id_desc(self):
        user1 = User(id=1)
        user2 = User(id=2)
        with transaction.manager:
            DBSession.add_all([user1, user2])
        user = User.newest()
        self.assertEqual(user.id, 2)

    def test_get_returns_record_filtered_by_criterion(self):
        user = User(id=1)
        with transaction.manager:
            DBSession.add(user)
        user = User.get(User.id == 1)
        self.assertIsInstance(user, User)

    def test_all_returns_multiple_matches_filtered_by_criterion(self):
        self.setup_test_data()
        clinics = Clinic.all(Clinic.id.in_([1, 2]))
        self.assertEqual(len(clinics), 2)

    def test_count_returns_count_filtered_by_criterion(self):
        self.setup_test_data()
        count = Clinic.count(Clinic.id.in_([1, 2]))
        self.assertEqual(count, 2)

    # TODO: this test belongs elsewehere
    def test_each_characteristic_has_a_characteristic_mapping(self):
        keys = [c[0] for c in constants.CHARACTERISTICS]
        mapping_keys = constants.CHARACTERISTIC_MAPPING.keys()
        self.assertTrue(all([k in mapping_keys for k in keys]))
