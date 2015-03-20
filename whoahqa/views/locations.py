from pyramid.view import (
    view_config,
    view_defaults,
)

from whoahqa.constants import characteristics as constants
from whoahqa.constants import permissions as perms
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
                 renderer='location_list.jinja2',
                 request_method='GET')
    def index(self):
        period = ReportingPeriod.get_current_period()
        return {
            'locations': Municipality.all(),
            'period': period,
            'key_indicators_key_labels': constants.INDICATOR_LABELS,
        }

    @view_config(name='',
                 context=Municipality,
                 renderer='clinics_summary.jinja2',
                 request_method='GET')
    def show(self):
        municipality = self.request.context
        clinics = municipality.clinics
        # TODO determine period based on what user selected.
        period = ReportingPeriod.get_current_period()

        return {
            'locations': clinics,
            'parent': municipality,
            'period': period,
            'key_indicators_key_labels': constants.INDICATOR_LABELS,
        }
