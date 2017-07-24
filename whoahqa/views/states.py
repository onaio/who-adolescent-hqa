from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults,
)

from whoahqa.constants import permissions as perms
from whoahqa.constants import groups
from whoahqa.models import (
    LocationFactory,
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
        user = self.request.user

        if user.group.name == groups.STATE_OFFICIAL:
            return HTTPFound(self.request.route_url(
                'states', traverse=(user.location.id)))

        return {
            'states': State.all(),
            'period': self.period,
            'periods': self.periods,
            'national_report': self.national_report(self.period),
            'key_indicators_key_labels': self.key_indicators_key_labels
        }

    @view_config(name='',
                 context=State,
                 renderer='state_summary.jinja2',
                 request_method='GET')
    def show(self):
        state = self.request.context

        return {
            'locations': state.children(),
            'key_indicators_key_labels': self.key_indicators_key_labels,
            'national_report': self.national_report(self.period),
            'period': self.period,
            'periods': self.periods,
            'state': state,
        }
