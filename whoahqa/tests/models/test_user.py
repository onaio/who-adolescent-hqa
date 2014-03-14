import datetime

from whoahqa.models import (
    OnaUser,
    ReportingPeriod,
    DBSession,
    User
)
from whoahqa.tests import TestBase


class TestUser(TestBase):
    def test_get_clinics(self):
        self.setup_test_data()
        user = OnaUser.get(OnaUser.username == 'manager_a').user

        clinics = user.get_clinics()
        self.assertEqual(len(clinics), 1)
        self.assertEqual(clinics[0].name, "Clinic A")

    def test_get_item_returns_reporting_period(self):
        self.setup_test_data()
        period = ReportingPeriod(
            title="2013/2014",
            start_date=datetime.datetime(2013, 3, 13),
            end_date=datetime.datetime(2014, 3, 13))
        DBSession.add(period)
        DBSession.flush()
        period = ReportingPeriod.newest()
        user = User.newest()
        selected_period = user.__getitem__(period.id)
        self.assertIsInstance(selected_period, ReportingPeriod)
        self.assertEqual(selected_period, period)

    def test_raise_key_error_when_invalid_period_id(self):
        self.setup_test_data()
        user = User.newest()
        self.assertRaises(KeyError, user.__getitem__, "abc")
