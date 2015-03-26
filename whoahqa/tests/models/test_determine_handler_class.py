import json

from whoahqa.constants import characteristics as constants
from whoahqa.models import (
    Submission,
    ZeroSubmissionHandlersError,
    MultipleSubmissionHandlersError,
    ClinicReportHandler,
    ClinicRegistrationHandler,
    determine_handler_class,
)
from whoahqa.tests import TestBase


class TestDetermineHandlerClass(TestBase):
    def test_return_clinic_report_handler_for_report_xforms(self):
        payload = self.submissions[0]
        submission = Submission(raw_data=json.loads(payload))
        handler_class = determine_handler_class(
            submission, Submission.HANDLER_TO_XFORMS_MAPPING)
        self.assertEqual(handler_class, ClinicReportHandler)

    def test_return_clinic_registration_handler_for_registration_xforms(self):
        payload = self.clinic_registrations[0]
        submission = Submission(raw_data=json.loads(payload))
        handler_class = determine_handler_class(
            submission, Submission.HANDLER_TO_XFORMS_MAPPING)
        self.assertEqual(handler_class, ClinicRegistrationHandler)

    def test_raise_multiple_submission_handlers_error_if_multiple_handlers(
            self):
        payload = self.submissions[0]
        handler_mapping = (
            (ClinicReportHandler, [constants.ADOLESCENT_CLIENT]),
            (ClinicRegistrationHandler, [constants.ADOLESCENT_CLIENT]),
        )
        submission = Submission(raw_data=json.loads(payload))
        self.assertRaises(MultipleSubmissionHandlersError,
                          determine_handler_class, submission, handler_mapping)

    def test_raise_zero_submission_handlers_error_if_no_handlers(self):
        payload = self.submissions[0]
        handler_mapping = ()
        submission = Submission(raw_data=json.loads(payload))
        self.assertRaises(ZeroSubmissionHandlersError,
                          determine_handler_class, submission, handler_mapping)
