import datetime

from pyramid import testing

from whoahqa.models import (
    DBSession,
    RootFactory,
    ReportingPeriodFactory,
    ReportingPeriod,)
from whoahqa.tests.test_base import TestBase


class TestReportingPeriodFactory(TestBase):
    def test_get_item_retrieves_by_slug(self):
        slug = '2014-2015'
        period = ReportingPeriod(
            title="2014/2015", slug=slug,
            start_date=datetime.date(2014, 2, 1),
            end_date=datetime.date(2015, 2, 1))
        DBSession.add(period)

        factory = ReportingPeriodFactory(
            testing.DummyRequest())
        period = factory.__getitem__(slug)
        self.assertEqual(period.slug, slug)
        self.assertEqual(period.__parent__, factory)
        self.assertEqual(period.__name__, slug)

    def test_get_item_throws_key_error_if_non_existent_slug(self):
        factory = ReportingPeriodFactory(
            testing.DummyRequest())
        self.assertRaises(KeyError, factory.__getitem__, 'non-existent')

