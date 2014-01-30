import unittest
import transaction

from webob.multidict import MultiDict
from pyramid import testing
from pyramid.paster import (
    get_appsettings
)
from pyramid.security import IAuthenticationPolicy
from sqlalchemy import engine_from_config
from webtest import TestApp

from whoahqa import main
from whoahqa.models import (
    DBSession,
    Base,
    BaseModel,
    UserFactory,
    ClinicFactory,
    user_clinics,
    User,
    Clinic
)
from whoahqa.views import (
    ClinicViews,
    UserViews
)


settings = get_appsettings('test.ini')
engine = engine_from_config(settings, 'sqlalchemy.')


class TestBase(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        # setup db
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine
        Base.metadata.drop_all()
        Base.metadata.create_all()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def setup_test_data(self):
        user = User()

        # add a couple of clinics
        clinic1 = Clinic(name="Clinic No. 1")
        # assign a user to clinic1
        user.clinics.append(clinic1)

        # leave clinic 2 unassigned
        clinic2 = Clinic(name="Clinic No. 2")

        with transaction.manager:
            DBSession.add_all([user, clinic1, clinic2])


class IntegrationTestBase(TestBase):
    def setUp(self):
        super(IntegrationTestBase, self).setUp()
        self.config.include('whoahqa')


class TestBaseModel(TestBase):
    def test_newest_returns_newest_record_by_id_desc(self):
        user1 = User(id=1)
        user2 = User(id=2)
        with transaction.manager:
            DBSession.add_all([user1, user2])
        user = User.newest()
        self.assertEqual(user.id, 2)


class TestUser(TestBase):
    def test_get_clinics(self):
        self.setup_test_data()
        user = User.newest()

        clinics = user.get_clinics()
        self.assertEqual(len(clinics), 1)
        self.assertEqual(clinics[0].name, "Clinic No. 1")


class TestClinic(TestBase):
    def test_assign_to_user(self):
        self.setup_test_data()
        user = User.newest()
        clinic = DBSession.query(Clinic).filter_by(name="Clinic No. 2").one()
        clinic.assign_to(user)
        user = DBSession.merge(user)
        clinic = DBSession.merge(clinic)
        self.assertEqual(clinic.user, user)


class TestUserFactory(TestBase):
    def test_get_item_returns_clinic_if_id_exists(self):
        self.setup_test_data()
        clinic = Clinic.newest()

        request = testing.DummyRequest()
        clinic = ClinicFactory(request).__getitem__(clinic.id)
        self.assertIsInstance(clinic, Clinic)

    def test_get_item_raises_key_error_if_id_doesnt_exist(self):
        # invalid clinic id
        clinic_id = -1

        request = testing.DummyRequest()
        self.assertRaises(KeyError,
                          ClinicFactory(request).__getitem__, clinic_id)


class TestClinicFactory(TestBase):
    def test_get_unassigned_clinics(self):
        self.setup_test_data()

        clinics = ClinicFactory.get_unassigned_clinics()
        self.assertEqual(len(clinics), 1)
        self.assertEqual(clinics[0].name, "Clinic No. 2")

    def test_get_item_returns_clinic_if_id_exists(self):
        self.setup_test_data()
        clinic = Clinic.newest()

        request = testing.DummyRequest()
        clinic = ClinicFactory(request).__getitem__(clinic.id)
        self.assertIsInstance(clinic, Clinic)

    def test_get_item_raises_key_error_if_id_doesnt_exist(self):
        # invalid user id
        clinic_id = -1

        request = testing.DummyRequest()
        self.assertRaises(KeyError,
                          ClinicFactory(request).__getitem__, clinic_id)


class TestClinicViews(IntegrationTestBase):
    def setUp(self):
        super(TestClinicViews, self).setUp()
        self.request = testing.DummyRequest()
        self.clinic_views = ClinicViews(self.request)

    def test_unassigned_clinics_view(self):
        self.setup_test_data()
        response = self.clinic_views.unassigned()

        # we should only have Clinic No. 2 in the response
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic No. 2")

    def test_assign_view(self):
        self.setup_test_data()
        user = User.newest()

        # get the unassigned clinic
        clinic = DBSession.query(Clinic).filter_by(name="Clinic No. 2").one()
        clinic_id = clinic.id
        self.request.context = clinic
        self.request.method = 'POST'
        self.request.user = user
        values = []
        self.request.POST = MultiDict(values)
        response = self.clinic_views.assign()

        # clinic should now be assigned to user
        count = DBSession.query(user_clinics).filter(
            user_clinics.columns.clinic_id == clinic_id).count()
        self.assertEqual(count, 1)


class TestUserViews(IntegrationTestBase):
    def test_user_clinics_view(self):
        self.setup_test_data()
        user = User.newest()
        request = testing.DummyRequest()
        request.context = user
        user_views = UserViews(request)
        response = user_views.clinics()

        # we should only have Clinic No. 1 in the response
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic No. 1")


class FunctionalTestBase(IntegrationTestBase):
    def setUp(self):
        super(FunctionalTestBase, self).setUp()
        app = main({}, **settings)
        self.testapp = TestApp(app)
        self.request = testing.DummyRequest()
        self.request.environ = {
            'SERVER_NAME': 'localhost'
        }


class TestViewsFunctional(FunctionalTestBase):
    def _login_user(self, user):
        policy = self.testapp.app.registry.queryUtility(IAuthenticationPolicy)
        headers = policy.remember(self.request, user.id)
        cookie_parts = dict(headers)['Set-Cookie'].split('; ')
        cookie = filter(
            lambda i: i.split('=')[0] == 'auth_tkt', cookie_parts)[0]
        return {'Cookie': cookie}

    def test_unassigned_clinics_view(self):
        url = self.request.route_path('clinics', traverse=('unassigned',))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_clinics_view(self):
        self.setup_test_data()
        url = self.request.route_path('users', traverse=('1', 'clinics'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_assign_clinic_view(self):
        self.setup_test_data()
        user = User.newest()
        headers = self._login_user(user)

        unassigned_clinic = ClinicFactory.get_unassigned_clinics()[0]
        url = self.request.route_path(
            'clinics', traverse=(unassigned_clinic.id, 'assign'))
        params = MultiDict([])
        response = self.testapp.post(url, params, headers=headers)