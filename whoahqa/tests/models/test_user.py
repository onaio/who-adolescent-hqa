from whoahqa.models import (
    OnaUser,
)
from whoahqa.tests import TestBase


class TestUser(TestBase):
    def test_get_clinics(self):
        self.setup_test_data()
        user = OnaUser.get(OnaUser.username == 'manager_a').user

        clinics = user.get_clinics()
        self.assertEqual(len(clinics), 1)
        self.assertEqual(clinics[0].name, "Clinic A")
