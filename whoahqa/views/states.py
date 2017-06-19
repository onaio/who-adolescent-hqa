from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults,
)

from whoahqa.constants import characteristics as constants
from whoahqa.constants import permissions as perms
from whoahqa.constants import groups
from whoahqa.views.helpers import get_period_from_request
from whoahqa.models import (
    Clinic,
    ClinicReport,
    LocationFactory,
    ReportingPeriod,
    State)
from whoahqa.views.base import BaseClassViews


@view_defaults(route_name='states',
               permission=perms.CAN_VIEW_STATE)
class StateViews(BaseClassViews):
    @view_config(name='',
                 context=LocationFactory,
                 renderer='states_list.jinja2',
                 request_method='GET')
    def index(self):
        period = get_period_from_request(self.request)
        ona_user = self.request.ona_user

        if ona_user.group.name == groups.STATE_OFFICIAL:
            return HTTPFound(self.request.route_url(
                'states', traverse=(ona_user.location.id)))

        clinics = Clinic.all()
        clinics = [c for c in clinics
                   if c.has_clinic_submissions_for_period(period.form_xpath)]

        national_report = ClinicReport.get_clinic_reports(
            clinics, period)

        return {
            'locations': State.all(),
            'period': period,
            'periods': ReportingPeriod.get_active_periods(),
            'national_report': national_report,
            'key_indicators_key_labels': constants.INDICATOR_LABELS
        }

    @view_config(name='',
                 context=State,
                 renderer='state_summary.jinja2',
                 request_method='GET')
    def show(self):
        state = self.request.context
        period = get_period_from_request(self.request)

        return {
            'locations': state.children(),
            'state': state,
            'period': period,
            'periods': ReportingPeriod.get_active_periods(),
            'key_indicators_key_labels': constants.INDICATOR_LABELS,
        }
