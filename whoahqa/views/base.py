from whoahqa.constants import characteristics as constants
from whoahqa.models import (
    Clinic,
    ClinicReport,
    ReportingPeriod)
from whoahqa.views.helpers import get_period_from_request


class BaseClassViews(object):
    def __init__(self, request):
        self.request = request
        self.period = get_period_from_request(request)
        self.periods = ReportingPeriod.get_active_periods()
        self.key_indicators_key_labels = constants.INDICATOR_LABELS

    def national_report(self, period):
        clinics = Clinic.all()
        clinics = [c for c in clinics
                   if c.has_clinic_submissions_for_period(period.form_xpath)]

        national_report = ClinicReport.get_clinic_reports(
            clinics, period)

        return national_report
