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
    def test_save_submission_with_valid_clinic_id(self):
        # create clinic with matching id
        clinic_code = "1A2B"
        clinic = Clinic(code=clinic_code, name="Clinic A")
        DBSession.add(clinic)

        # check current counts
        count = Submission.count()
        clinic_submission_count = ClinicSubmission.count()
        test_data = self.submissions[0]
        Submission.create_from_json(test_data)
        submission = Submission.newest()
        self.assertEqual(Submission.count(), count + 1)
        self.assertEqual(submission.raw_data, json.loads(test_data))

        # check that a clinic_submission record was created
        self.assertEqual(ClinicSubmission.count(), clinic_submission_count + 1)

    def test_save_submission_with_multiple_characteristics(self):
        # create clinic with matching id
        clinic_code = "1A2B"
        clinic = Clinic(code=clinic_code, name="Clinic A")
        DBSession.add(clinic)

        # check current counts
        count = Submission.count()
        clinic_submission_count = ClinicSubmission.count()
        test_data = self.submissions[2]
        Submission.create_from_json(test_data)
        submission = Submission.newest()
        self.assertEqual(Submission.count(), count + 1)
        self.assertEqual(submission.raw_data, json.loads(test_data))

        # check that 2 clinic_submission record was created
        self.assertEqual(ClinicSubmission.count(), clinic_submission_count + 2)

    def test_save_submission_with_invalid_clinic_id(self):
        count = Submission.count()
        clinic_submissions_count = ClinicSubmission.count()
        test_data = self.submissions[1]

        self.assertRaises(ClinicNotFound, Submission.create_from_json,
                          test_data)

        submission = Submission.newest()
        self.assertEqual(Submission.count(), count + 1)
        self.assertEqual(submission.raw_data, json.loads(test_data))
        self.assertEqual(clinic_submissions_count,
                         ClinicSubmission.count())

    def test_parse_json(self):
        parsed_json = Submission.parse_json(self.submissions[0])
        # we expect a structure with the determined clinic id (characteristics,
        # mapping of client tools to form ids)
        self.assertEqual(
            parsed_json,
            ("1A2B", ["twenty"], "health_facility_manager_interview_EnSp",))
