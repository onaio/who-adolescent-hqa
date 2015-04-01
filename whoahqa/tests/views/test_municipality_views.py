import datetime
import transaction
from pyramid import testing
from mock import patch

from whoahqa.models import (
    Clinic,
    DBSession,
    Municipality,
    OnaUser,
    ReportingPeriod)
from whoahqa.tests.test_base import IntegrationTestBase
from whoahqa.views import MunicipalityViews


class TestMunicipalityViews(IntegrationTestBase):
    def setUp(self):
        super(TestMunicipalityViews, self).setUp()
        self.request = testing.DummyRequest()
        self.view = MunicipalityViews(self.request)
        self._create_user('municipality-manager')

        with transaction.manager:
            reporting_period = ReportingPeriod(
                title='Period 1',
                start_date=datetime.datetime(2015, 5, 1),
                end_date=datetime.datetime(2015, 7, 31))

            reporting_period.save()

            municipality = Municipality(name="Brasillia")
            DBSession.add(municipality)
            for i in range(5):
                clinic = Clinic(name="Clinic {}".format(i),
                                code="{}BCDE".format(i),
                                municipality=municipality)
                DBSession.add(clinic)

        self.request.ona_user = OnaUser.get(
            OnaUser.username == 'municipality-manager')

    def test_municipality_index(self):
        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 6, 1)
            response = self.view.index()

            locations = response['locations']
            self.assertEquals(locations, Municipality.all())
            self.assertNotEquals(len(locations), 0)

    def test_municipality_show(self):
        municipality = Municipality.get(Municipality.name == "Brasillia")
        self.request.context = municipality

        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 6, 1)
            response = self.view.show()

            self.assertEqual(response['municipality'], municipality)
            self.assertEqual(response['locations'], municipality.clinics)
            self.assertNotEqual(len(response['locations']), 0)
