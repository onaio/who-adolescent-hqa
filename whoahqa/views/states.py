from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults,
)

from whoahqa.constants import characteristics as constants
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
        ona_user = self.request.ona_user

        if ona_user.group.name == groups.STATE_OFFICIAL:
            return HTTPFound(self.request.route_url(
                'states', traverse=(ona_user.location.id)))

        national_report = self.national_report(self.period)

        return {
            'locations': State.all(),
            'period': self.period,
            'periods': self.periods,
            'national_report': national_report,
            'key_indicators_key_labels': constants.INDICATOR_LABELS
        }

    @view_config(name='',
                 context=State,
                 renderer='state_summary.jinja2',
                 request_method='GET')
    def show(self):
        state = self.request.context

        national_report = self.national_report(self.period)

        return {
            'locations': state.children(),
            'key_indicators_key_labels': constants.INDICATOR_LABELS,
            'national_report': national_report,
            'period': self.period,
            'periods': self.periods,
            'state': state,
        }
