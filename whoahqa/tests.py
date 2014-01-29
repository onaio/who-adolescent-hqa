import unittest
import transaction

from pyramid import testing
from pyramid.paster import (
    get_appsettings
)

from sqlalchemy import engine_from_config

from whoahqa.models import (
    DBSession,
    Base,
    BaseModel,
    UserFactory,
    ClinicFactory,
    User,
    Clinic
)

from whoahqa.views import (
    unassigned_clinics,
    user_clinics
)


settings = get_appsettings('test.ini')
engine = engine_from_config(settings, 'sqlalchemy.')
DBSession.configure(bind=engine)


class TestBase(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('whoahqa')
        # setup db
        Base.metadata.bind = engine
        Base.metadata.drop_all()
        Base.metadata.create_all()

    def tearDown(self):
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


class TestBaseModel(TestBase):
    def test_newest_returns_newest_record_by_id_desc(self):
        user1 = User(id=1)
        user2 = User(id=2)
        with transaction.manager:
            DBSession.add_all([user1, user2])
        user = User.newest()
        self.assertEqual(user.id, 2)


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

    def test_get_item_returns_user_if_id_exists(self):
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

    def test_get_user_clinics(self):
        self.setup_test_data()
        user = User.newest()

        clinics = ClinicFactory.get_user_clinics(user)
        self.assertEqual(len(clinics), 1)
        self.assertEqual(clinics[0].name, "Clinic No. 1")


class TestClinicView(TestBase):
    def test_unassigned_clinic_view(self):
        self.setup_test_data()

        request = testing.DummyRequest()
        response = unassigned_clinics(request)

        # we should only have Clinic No. 2 in the response
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic No. 2")

    def test_user_clinics_view(self):
        self.setup_test_data()
        user = User.newest()
        request = testing.DummyRequest()
        request.context = user
        response = user_clinics(request)

        # we should only have Clinic No. 1 in the response
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic No. 1")
