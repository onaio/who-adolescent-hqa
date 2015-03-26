import datetime

from whoahqa.tests import TestBase
from whoahqa.models import ReportingPeriod


class TestReportingPeriod(TestBase):
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
