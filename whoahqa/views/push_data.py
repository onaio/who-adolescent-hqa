from pyramid.view import (
    view_config,
)
from pyramid.security import NO_PERMISSION_REQUIRED
from whoahqa.constants import permissions as perms
from whoahqa.models import (
    DBSession,
    ReportingPeriod,
    State,
    Location)

from ..utils import normalizeString, format_location_name as fmt, xstr


@view_config(
    route_name='push',
    match_param='action=clinics.csv',
    request_method='GET',
    renderer='csv',
    permission=NO_PERMISSION_REQUIRED)
def push_facilities(request):
    states = DBSession.query(State).order_by("name asc").all()

    header = ['CNES', 'state', 'municipality', 'facility_name']
    rows = []

    for state in states:
        municipalities = state.children()

        for municipality in municipalities:
            clinics = municipality.children()

            for clinic in clinics:
                if clinic is not None:
                    clinic_name = normalizeString(clinic.name)
                    clinic_cnes = clinic.code
                    municipality_name = normalizeString(municipality.name)
                    state_name = normalizeString(state.name)
                    rows.append([
                        clinic_cnes,
                        fmt(state_name),
                        fmt(municipality_name),
                        fmt(clinic_name)])

    filename = 'clinics.csv'
    request.response.content_disposition = 'attachment;filename=' + filename

    return {
        'header': header,
        'rows': rows
    }


@view_config(
    route_name='push',
    match_param='action=periods.csv',
    request_method='GET',
    renderer='csv',
    permission=NO_PERMISSION_REQUIRED)
def push_report_periods(request):
    header = ['reporting_period']
    rows = []

    reporting_periods = ReportingPeriod.get_active_periods()

    [rows.append([period.form_xpath]) for period in reporting_periods]

    return {
        'header': header,
        'rows': rows
    }


@view_config(
    route_name='push',
    match_param='action=locations.csv',
    request_method='GET',
    renderer='csv',
    permission=perms.CAN_LIST_STATE)
def push_locations(request):
    locations = Location.all()
    header = ['name', 'location_type', 'parent']
    rows = []

    for location in locations:
        rows.append([
            location.name,
            location.location_type,
            xstr(location.parent)])

    return {
        'header': header,
        'rows': rows
    }
