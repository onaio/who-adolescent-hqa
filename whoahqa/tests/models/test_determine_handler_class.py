import json

from whoahqa import constants
from whoahqa.models import (
    Submission,
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

    def test_raise_value_error_if_multiple_handlers(self):
        payload = self.submissions[0]
        handler_mapping = (
            (ClinicReportHandler, [constants.COMMUNITY_MEMBER]),
            (ClinicRegistrationHandler, [constants.COMMUNITY_MEMBER]),
        )
        submission = Submission(raw_data=json.loads(payload))
        self.assertRaises(
            ValueError, determine_handler_class, submission, handler_mapping)
