import json

from whoahqa.tests import TestBase
from whoahqa.models import (
    DBSession,
    Submission,
    Clinic,
    ClinicSubmission,
    ClinicNotFound,
    ClinicReportHandler
)


class TestClinicSubmissionHandler(TestBase):
    def test_save_submission_with_valid_clinic_id(self):
        # create clinic with matching id
        clinic_code = "1A2B"
        clinic = Clinic(code=clinic_code, name="Clinic A")
        DBSession.add(clinic)

        payload = self.submissions[0]
        submission = Submission(raw_data=json.loads(payload))
        count = ClinicSubmission.count()
        ClinicReportHandler(submission).handle_submission()

        # check that a clinic_submission record was created
        self.assertEqual(ClinicSubmission.count(), count + 1)

    def test_save_submission_with_multiple_characteristics(self):
        # create clinic with matching id
        clinic_code = "1A2B"
        clinic = Clinic(code=clinic_code, name="Clinic A")
        DBSession.add(clinic)

        # check current counts
        count = ClinicSubmission.count()
        payload = self.submissions[2]
        submission = Submission(raw_data=json.loads(payload))
        ClinicReportHandler(submission).handle_submission()

        # check that 2 clinic_submission record was created
        self.assertEqual(ClinicSubmission.count(), count + 2)

    def test_save_submission_with_invalid_clinic_id(self):
        clinic_submissions_count = ClinicSubmission.count()
        payload = self.submissions[1]

        submission = Submission(raw_data=json.loads(payload))
        self.assertRaises(
            ClinicNotFound,
            ClinicReportHandler(submission).handle_submission)
        self.assertEqual(clinic_submissions_count, ClinicSubmission.count())

    def test_parse_data(self):
        raw_data = json.loads(self.submissions[0])
        parsed_data = ClinicReportHandler.parse_data(raw_data)
        # we expect a structure with the determined clinic id (characteristics,
        # mapping of client tools to form ids)
        self.assertEqual(
            parsed_data,
            ("1A2B", ["twenty"], "health_facility_manager_interview",))
