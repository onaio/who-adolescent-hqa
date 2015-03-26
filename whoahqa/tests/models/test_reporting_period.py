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

    def test_generate_form_key(self):
        """
        1may_31jul_2015 <=> 1 May - 31 Jul 2015
        1aug_31oct_2015 <=> 1 Aug - 31 Oct 2015
        1nov_2015_31jan_2016  <=>  1 Nov 2015 - 31 Jan 2016
        1feb_30apr_2016 <=> 1 Feb - 30 Apr 2016

        """
        reporting_period = ReportingPeriod(
            title="bla",
            start_date=datetime.date(2015, 5, 1),
            end_date=datetime.date(2015, 7, 31))

        self.assertEqual(reporting_period.generate_form_key(),
                         "1may_31jul_2015")

        reporting_period = ReportingPeriod(
            title="ble",
            start_date=datetime.date(2015, 8, 1),
            end_date=datetime.date(2015, 10, 31))
        self.assertEqual(reporting_period.generate_form_key(),
                         "1aug_31oct_2015")

        reporting_period = ReportingPeriod(
            title="bli",
            start_date=datetime.date(2015, 11, 1),
            end_date=datetime.date(2016, 1, 31))
        self.assertEqual(reporting_period.generate_form_key(),
                         "1nov_2015_31jan_2016")

        reporting_period = ReportingPeriod(
            title="bli",
            start_date=datetime.date(2016, 2, 1),
            end_date=datetime.date(2016, 4, 30))
        self.assertEqual(reporting_period.generate_form_key(),
                         "1feb_30apr_2016")

    def setup_reporting_periods(self):
        self.reporting_period1 = ReportingPeriod(
            title="test 1",
            start_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 2, 1))
        self.reporting_period2 = ReportingPeriod(
            title="test 2",
            start_date=datetime.date(2015, 2, 1),
            end_date=datetime.date(2015, 3, 1))
        self.reporting_period3 = ReportingPeriod(
            title="test 3",
            start_date=datetime.date(2015, 4, 1),
            end_date=datetime.date(2015, 5, 1))

        DBSession.add_all([self.reporting_period1,
                           self.reporting_period2,
                           self.reporting_period3])

    # filter reporting periods when current date is 1st March 2015
    def test_get_active_periods_when_month_is_1st_march(self):
        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 3, 1)
            active_periods = ReportingPeriod.get_active_periods()

            self.assertEqual(len(active_periods), 2)
            self.assertNotIn(self.reporting_period3, active_periods)

    # filter reporting periods when current date is 31st Jan 2015
    def test_get_active_periods_when_month_is_feb(self):
        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 1, 31)
            active_periods = ReportingPeriod.get_active_periods()
            self.assertEqual(len(active_periods), 1)
            self.assertIn(self.reporting_period1, active_periods)

    # filter reporting periods when current date is 30th May 2015
    def test_get_active_periods_when_month_is_may(self):
        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 5, 30)
            active_periods = ReportingPeriod.get_active_periods()
            self.assertEqual(len(active_periods), 3)
