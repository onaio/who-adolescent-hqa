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
    User,
    Clinic,
    ClinicFactory
)

from whoahqa.views import unassigned_clinics


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

    def create_test_clinics(self):
        user = User()

        # add a couple of clinics
        clinic1 = Clinic(name="Clinic No. 1")
        # assign a user to clinic1
        user.clinics.append(clinic1)

        # leave clinic 2 unassigned
        clinic2 = Clinic(name="Clinic No. 2")

        with transaction.manager:
            DBSession.add_all([user, clinic1, clinic2])


class TestClinicFactory(TestBase):
    def test_get_unassigned_clinics(self):
        self.create_test_clinics()

        clinics = ClinicFactory.get_unassigned_clinics()
        self.assertEqual(len(clinics), 1)
        self.assertEqual(clinics[0].name, "Clinic No. 2")


class TestClinicView(TestBase):
    def test_unassigned_clinic_view(self):
        self.create_test_clinics()

        request = testing.DummyRequest()
        response = unassigned_clinics(request)

        # we should only Clinic No. 2 in the response
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic No. 2")



