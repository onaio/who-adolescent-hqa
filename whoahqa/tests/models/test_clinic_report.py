from whoahqa.models import (
    Clinic,
    ClinicReport,
    ReportingPeriod)
from whoahqa.tests import TestBase


class TestClinicReports(TestBase):
    def setUp(self):
        super(TestClinicReports, self).setUp()
        self.setup_test_data()
        self.create_brazil_submissions()

    def test_clinic_report_is_generated_if_none_existent(self):
        count = ClinicReport.count()
        clinic = Clinic.get(Clinic.id == 1)
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')

        ClinicReport.get_or_generate(clinic, period)

        self.assertEqual(ClinicReport.count(), count + 1)
