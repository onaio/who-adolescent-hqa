import json

from whoahqa.models import (
    DBSession,
    ClinicNotFound,
    ClinicSubmission,
    Clinic,
    Submission,
)
from whoahqa.tests import TestBase


class TestSubmission(TestBase):
    def test_create_clinic_submission_from_json(self):
        # create clinic with matching id
        clinic_code = "1A2B"
        clinic = Clinic(code=clinic_code, name="Clinic A")
        DBSession.add(clinic)

        # check current counts
        count = Submission.count()
        clinic_submission_count = ClinicSubmission.count()
        payload = self.submissions[0]
        Submission.create_from_json(payload)
        submission = Submission.newest()
        self.assertEqual(Submission.count(), count + 1)
        self.assertEqual(submission.raw_data, json.loads(payload))

        # check that a clinic_submission record was created
        self.assertEqual(ClinicSubmission.count(), clinic_submission_count + 1)

    def test_register_clinic_from_json(self):
        # check current counts
        count = Submission.count()
        clinic_count = Clinic.count()
        payload = self.clinic_registrations[0]
        Submission.create_from_json(payload)
        submission = Submission.newest()
        self.assertEqual(Submission.count(), count + 1)
        self.assertEqual(submission.raw_data, json.loads(payload))

        # check that a clinic record was created
        self.assertEqual(Clinic.count(), clinic_count + 1)
