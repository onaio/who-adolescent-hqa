from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults,
)

from whoahqa.constants import permissions as perms
from whoahqa.constants import groups
from whoahqa.models import (
    LocationFactory,
    Municipality)
from whoahqa.views.base import BaseClassViews


@view_defaults(route_name='municipalities',
               permission=perms.CAN_LIST_MUNICIPALITY)
class MunicipalityViews(BaseClassViews):
    @view_config(name='',
                 context=LocationFactory,
                 renderer='municipalities_list.jinja2',
                 request_method='GET')
    def index(self):
        user = self.request.user

        if user.group.name == groups.MUNICIPALITY_MANAGER:
            return HTTPFound(self.request.route_url(
                'municipalities', traverse=(user.location.id)))

        return {
            'locations': Municipality.all(),
            'national_report': self.national_report(self.period),
            'period': self.period,
            'periods': self.periods,
            'key_indicators_key_labels': self.key_indicators_key_labels,
        }

    @view_config(name='',
                 context=Municipality,
                 permission=perms.CAN_VIEW_MUNICIPALITY,
                 renderer='municipality_summary.jinja2',
                 request_method='GET')
    def show(self):
        municipality = self.request.context
        clinics = municipality.clinics

        return {
            'locations': clinics,
            'national_report': self.national_report(self.period),
            'municipality': municipality,
            'state': municipality.parent,
            'period': self.period,
            'periods': self.periods,
            'key_indicators_key_labels': self.key_indicators_key_labels,
        }
