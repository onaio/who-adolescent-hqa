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
    State,
    ReportingPeriod,
    User)
from whoahqa.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase)
from whoahqa.views import StateViews


class TestStateViews(IntegrationTestBase):
    def setUp(self):
        super(TestStateViews, self).setUp()
        self.request = testing.DummyRequest()
        self.view = StateViews(self.request)
        self._create_user('state-official')

        with transaction.manager:
            reporting_period = ReportingPeriod(
                title='Period 1',
                start_date=datetime.datetime(2015, 5, 1),
                end_date=datetime.datetime(2015, 7, 31))

            reporting_period.save()
            state = State(name="Sao Paolo")
            municipality1 = Municipality(name="Brasillia", parent=state)
            municipality2 = Municipality(name="Brasil", parent=state)
            DBSession.add_all([state, municipality1, municipality2])
            for i in range(5):
                clinic = Clinic(name="Clinic {}".format(i),
                                code="{}BCDE".format(i),
                                municipality=municipality1)
                DBSession.add(clinic)

        self.request.user = OnaUser.get(
            OnaUser.username == 'state-official').user

    def test_states_index(self):
        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 6, 1)
            response = self.view.index()

            locations = response['locations']
            self.assertEquals(locations, State.all())
            self.assertNotEquals(len(locations), 0)

    def test_state_show(self):
        state = State.get(State.name == "Sao Paolo")
        self.request.context = state

        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 6, 1)
            response = self.view.show()

            self.assertEqual(response['state'], state)
            self.assertEqual(response['locations'], Municipality.all(
                Municipality.name.in_(['Brasil', 'Brasillia'])))
            self.assertNotEqual(len(response['locations']), 0)


class TestStateViewsFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestStateViewsFunctional, self).setUp()

        with transaction.manager:
            state = State(name="Sao Paolo")
            municipality1 = Municipality(name="Brasillia", parent=state)
            municipality2 = Municipality(name="Brasil", parent=state)

            user_group = Group(name="state_official")
            user = User()
            user.group = user_group
            user.location = state

            ona_user = OnaUser(username="state-official",
                               user=user,
                               refresh_token="1239khyackas")

            ona_user.save()

            reporting_period = ReportingPeriod(
                title='Period 1',
                start_date=datetime.datetime(2015, 5, 1),
                end_date=datetime.datetime(2015, 7, 31))

            reporting_period.save()
            DBSession.add_all([state, municipality1, municipality2])

    def test_state_index_with_non_authorised_user(self):
        self._create_user("johndoe")
        url = self.request.route_path('states', traverse=())
        headers = self._login_user("johndoe")
        response = self.testapp.get(url, headers=headers, status=403)
        self.assertEqual(response.status_code, 403)

    def test_state_show_with_authorised_user(self):
        state = State.get(State.name == "Sao Paolo")
        url = self.request.route_path('states', traverse=(state.id))
        headers = self._login_user("state-official")

        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 6, 1)
            response = self.testapp.get(url, headers=headers)
            self.assertEqual(response.status_code, 200)

    def test_state_show_for_user_without_perms(self):
        state = State.get(State.name == "Sao Paolo")
        self._create_user('renegade', 'state_official')
        url = self.request.route_path('states', traverse=(state.id))
        headers = self._login_user("renegade")

        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 6, 1)
            response = self.testapp.get(url, headers=headers, status=403)
            self.assertEqual(response.status_code, 403)
