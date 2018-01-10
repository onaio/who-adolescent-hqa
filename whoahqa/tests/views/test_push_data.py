import datetime

from pyramid import testing
from whoahqa.tests import IntegrationTestBase
from whoahqa.models import Clinic, Municipality, ReportingPeriod, State
from whoahqa.views.push_data import push_facilities, push_report_periods


class TestPushData(IntegrationTestBase):

    def setUp(self):
        super(TestPushData, self).setUp()
        self.request = testing.DummyRequest()

    def test_push_facilities_with_empty_locations(self):
        response = push_facilities(self.request)

        self.assertListEqual(
            response['header'],
            ['CNES', 'state', 'municipality', 'facility_name'])

        self.assertEqual(0, len(response['rows']))

    def test_push_facilities_with_locations(self):
        # create dummy data
        self._create_state()
        self._create_municipality()

        municipality = Municipality.newest()
        state = State.newest()
        municipality.parent = state
        municipality.save()

        clinic1 = Clinic(id=1,
                         name=u"Clinic A",
                         code="1A2B",
                         municipality=municipality)
        clinic1.save()

        # test push_facilities service
        response = push_facilities(self.request)

        self.assertEqual(1, len(response['rows']))

    def test_push_report_periods_without_data(self):
        response = push_report_periods(self.request)

        self.assertListEqual(
            response['header'],
            ['reporting_period'])

        self.assertEqual(0, len(response['rows']))

    def test_push_report_periods_with_data(self):
        reporting_period1 = ReportingPeriod(
            title='Period 1',
            form_xpath='2017',
            start_date=datetime.datetime(2017, 1, 1),
            end_date=datetime.datetime(2017, 12, 31))
        reporting_period2 = ReportingPeriod(
            title='Period 2',
            form_xpath='2018',
            start_date=datetime.datetime(2018, 1, 1),
            end_date=datetime.datetime(2018, 12, 31))

        reporting_period3 = ReportingPeriod(
            title='Period 3',
            form_xpath='2019',
            start_date=datetime.datetime(2019, 1, 1),
            end_date=datetime.datetime(2019, 12, 31))

        reporting_period1.save()
        reporting_period2.save()
        reporting_period3.save()

        response = push_report_periods(self.request)
        self.assertEqual(3, len(response['rows']))
        self.assertEqual(['2017'], response['rows'][0])
        self.assertEqual(['2018'], response['rows'][1])
        self.assertEqual(['2019'], response['rows'][2])

    def test_push_report_periods_when_old_periods_present(self):
        reporting_period1 = ReportingPeriod(
            title='Period 1',
            form_xpath='2016',
            start_date=datetime.datetime(2016, 1, 1),
            end_date=datetime.datetime(2016, 12, 31))
        reporting_period2 = ReportingPeriod(
            title='Period 2',
            form_xpath='2017',
            start_date=datetime.datetime(2017, 1, 1),
            end_date=datetime.datetime(2017, 12, 31))
        reporting_period3 = ReportingPeriod(
            title='Period 3',
            form_xpath='2018',
            start_date=datetime.datetime(2018, 1, 1),
            end_date=datetime.datetime(2018, 12, 31))

        reporting_period1.save()
        reporting_period2.save()
        reporting_period3.save()

        response = push_report_periods(self.request)
        self.assertEqual(3, len(response['rows']))
        self.assertEqual(['2016'], response['rows'][0])
        self.assertEqual(['2017'], response['rows'][1])
        self.assertEqual(['2018'], response['rows'][2])
