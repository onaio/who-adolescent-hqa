import transaction

from whoahqa.models import (
    Clinic,
    ClinicReport,
    ReportingPeriod)
from whoahqa.tests import TestBase


class TestClinicReports(TestBase):
    def setUp(self):
        super(TestClinicReports, self).setUp()
        self.setup_test_data()
        self.create_adolescent_client_submissions_v2()

    def create_clinic_report(self):
        clinic = Clinic.get(Clinic.id == 3)
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')

        with transaction.manager:
            ClinicReport.get_or_generate(clinic, period)

    def test_clinic_report_is_generated_if_none_existent(self):
        count = ClinicReport.count()
        clinic = Clinic.get(Clinic.id == 3)
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')

        ClinicReport.get_or_generate(clinic, period)

        self.assertEqual(ClinicReport.count(), count + 1)

    def test_clinic_report_catches_key_indicators(self):
        self.create_clinic_report()
        report = ClinicReport.newest()

        key_indicators = report.get_key_indicators()
        self.assertEqual(key_indicators['equitable'], 7.228327228327228)
