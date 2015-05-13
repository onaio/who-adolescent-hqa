import datetime

from mock import patch

from whoahqa.tests import TestBase
from whoahqa.models import (
    DBSession,
    ReportingPeriod)


class TestReportingPeriod(TestBase):
    def setUp(self):
        super(TestReportingPeriod, self).setUp()
        self.setup_reporting_periods()

    def setup_reporting_periods(self):
        self.reporting_period1 = ReportingPeriod(
            title="test 1",
            form_xpath="jan_2015feb_2015",
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 2, 1))
        self.reporting_period2 = ReportingPeriod(
            title="test 2",
            form_xpath="feb_2015mar_2015",
            start_date=datetime.date(2015, 2, 1),
            end_date=datetime.date(2015, 3, 1))
        self.reporting_period3 = ReportingPeriod(
            title="test 3",
            form_xpath="apr_2015may_2015",
            start_date=datetime.date(2015, 4, 1),
            end_date=datetime.date(2015, 5, 1))

        DBSession.add_all([self.reporting_period1,
                           self.reporting_period2,
                           self.reporting_period3])

    # filter reporting periods when current date is 1st March 2015
    # def test_get_active_periods_when_month_is_1st_march(self):
    #     with patch('whoahqa.models.reporting_period.get_current_date') as mock:  # noqa
    #         mock.return_value = datetime.date(2015, 3, 1)
    #         active_periods = ReportingPeriod.get_active_periods()

    #         self.assertEqual(len(active_periods), 2)
    #         self.assertNotIn(self.reporting_period3, active_periods)

    # # filter reporting periods when current date is 31st Jan 2015
    # def test_get_active_periods_when_month_is_feb(self):
    #     with patch('whoahqa.models.reporting_period.get_current_date') as mock:  # noqa
    #         mock.return_value = datetime.date(2015, 1, 31)
    #         active_periods = ReportingPeriod.get_active_periods()
    #         self.assertEqual(len(active_periods), 1)
    #         self.assertIn(self.reporting_period1, active_periods)

    # filter reporting periods when current date is 30th May 2015
    def test_get_active_periods_when_month_is_may(self):
        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 5, 30)
            active_periods = ReportingPeriod.get_active_periods()
            self.assertEqual(len(active_periods), 3)
