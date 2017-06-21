from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults,
)

from whoahqa.constants import permissions as perms, groups
from whoahqa.models import (
    User,
    ReportingPeriod
)
from whoahqa.views.base import BaseClassViews


@view_defaults(route_name='users')
class UserViews(BaseClassViews):

    @view_config(name='clinics',
                 renderer='clinics_summary.jinja2',
                 permission=perms.CAN_LIST_CLINICS,
                 context=User)
    def clinics(self):
        user = self.request.context

        if user.group.name == groups.NATIONAL_OFFICIAL:
            url = self.request.route_url('states', traverse=(),
                                         _query={'period': self.period.id})
            HTTPFound(url)

        clinics = user.get_clinics()

        municipality = user.get_municipality_from_clinics()

        return {
            'period': self.period,
            'periods': self.periods,
            'municipality': municipality,
            'locations': clinics,
            'key_indicators_key_labels': self.key_indicators_key_labels
        }

    @view_config(name='select-period',
                 renderer='reporting_period_select.jinja2',
                 permission=perms.AUTHENTICATED,
                 context=User)
    def select_reporting_period(self):
        user = self.request.context
        periods = ReportingPeriod.all()
        url_target = self.request.GET.get('came_from')
        return {'periods': periods, 'user': user, 'url_target': url_target}
