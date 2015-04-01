import datetime
import transaction
from pyramid import testing
from mock import patch

from whoahqa.models import (
    Clinic,
    DBSession,
    Group,
    Municipality,
    OnaUser,
    ReportingPeriod,
    State,
    User)
from whoahqa.tests.test_base import (
    FunctionalTestBase,
    IntegrationTestBase)
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


class TestMunicipalityViewsFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestMunicipalityViewsFunctional, self).setUp()

        with transaction.manager:
            state = State(name="Sao Paolo")
            municipality1 = Municipality(name="Brasillia", parent=state)
            municipality2 = Municipality(name="Brasil", parent=state)

            user_group = Group(name="municipality_official")
            user = User()
            user.group = user_group
            user.location = municipality1

            ona_user = OnaUser(username="m-official",
                               user=user,
                               refresh_token="1239khyackas")

            ona_user.save()

            reporting_period = ReportingPeriod(
                title='Period 1',
                start_date=datetime.datetime(2015, 5, 1),
                end_date=datetime.datetime(2015, 7, 31))

            reporting_period.save()
            DBSession.add_all([state, municipality1, municipality2])

    def test_can_access_own_municipality(self):
        municipality = Municipality.get(Municipality.name == "Brasillia")
        url = self.request.route_path(
            'municipalities', traverse=(municipality.id))
        headers = self._login_user("m-official")

        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 6, 1)
            response = self.testapp.get(url, headers=headers)
            self.assertEqual(response.status_code, 200)
