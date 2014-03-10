import datetime

from pyramid import testing

from whoahqa.models import (
    DBSession,
    RootFactory,
    ReportingPeriodFactory,
    ReportingPeriod,)
from whoahqa.tests.test_base import TestBase


class TestReportingPeriodFactory(TestBase):
    def test_get_item_retrieves_by_id(self):
        period = ReportingPeriod(
            title="2014/2015",
            start_date=datetime.date(2014, 2, 1),
            end_date=datetime.date(2015, 2, 1))
        DBSession.add(period)
        DBSession.flush()
        id = period.id

        factory = ReportingPeriodFactory(
            testing.DummyRequest())
        period = factory.__getitem__(id)
        self.assertEqual(period.id, id)
        self.assertEqual(period.__parent__, factory)
        self.assertEqual(period.__name__, id)

    def test_get_item_throws_key_error_if_non_existent_id(self):
        factory = ReportingPeriodFactory(
            testing.DummyRequest())
        self.assertRaises(KeyError, factory.__getitem__, '0')

