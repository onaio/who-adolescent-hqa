import json

from whoahqa import constants
from whoahqa.utils import hashid
from whoahqa.models import (
    DBSession,
    User,
    Submission,
    Clinic,
    UserNotFound,
    ClinicRegistrationHandler
)
from whoahqa.tests import TestBase


class TestClinicRegistrationHandler(TestBase):
    def test_create_clinic_from_submission(self):
        # create user with matching id
        DBSession.add(User())
        user = User.newest()

        payload = self.clinic_registrations[0]
        raw_data = json.loads(payload)
        raw_data[constants.USER_ID] = user.id
        submission = Submission(raw_data=raw_data)
        count = Clinic.count()
        ClinicRegistrationHandler(submission).handle_submission()

        # check that a clinic_submission record was created
        self.assertEqual(Clinic.count(), count + 1)

        # make sure the decrypted code is equal to the clinic's id
        clinic = Clinic.newest()
        self.assertEqual((clinic.id,), hashid.decrypt(clinic.code))

    def test_creates_unassigned_clinic_if_user_doesnt_exist(self):
        payload = self.clinic_registrations[0]
        raw_data = json.loads(payload)
        count = Clinic.count()
        submission = Submission(raw_data=raw_data)
        self.assertRaises(
            UserNotFound,
            ClinicRegistrationHandler(submission).handle_submission)

        # check that a clinic_submission record was NOT created
        self.assertEqual(Clinic.count(), count + 1)

    def test_parse_data(self):
        raw_data = json.loads(self.clinic_registrations[0])
        parsed_data = ClinicRegistrationHandler.parse_data(raw_data)
        # we expect a user_id and clinic name
        self.assertEqual(
            parsed_data,
            ("2", "New Kakamega Clinic",))
