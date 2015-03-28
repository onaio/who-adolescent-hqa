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
    LocationFactory,
    Municipality,
    ReportingPeriod)
from whoahqa.views.base import BaseClassViews


@view_defaults(route_name='municipalities',
               permission=perms.CAN_LIST_MUNICIPALITY)
class MunicipalityViews(BaseClassViews):
    @view_config(name='',
                 context=LocationFactory,
                 renderer='municipalities_list.jinja2',
                 request_method='GET')
    def index(self):
        period = get_period_from_request(self.request)
        ona_user = self.request.ona_user

        if ona_user.group.name == groups.MUNICIPALITY_MANAGER:
            return HTTPFound(self.request.route_url(
                'municipalities', traverse=(ona_user.location.id)))

        return {
            'locations': Municipality.all(),
            'period': period,
            'periods': ReportingPeriod.get_active_periods(),
            'key_indicators_key_labels': constants.INDICATOR_LABELS,
        }

    @view_config(name='',
                 context=Municipality,
                 renderer='clinics_summary.jinja2',
                 request_method='GET')
    def show(self):
        municipality = self.request.context
        clinics = municipality.clinics
        period = get_period_from_request(self.request)

        return {
            'locations': clinics,
            'parent': municipality,
            'period': period,
            'periods': ReportingPeriod.get_active_periods(),
            'key_indicators_key_labels': constants.INDICATOR_LABELS,
        }
