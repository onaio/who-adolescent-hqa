from pyramid.view import (
    view_config,
    view_defaults,
)

from whoahqa.constants import characteristics as constants
from whoahqa.constants import permissions as perms
from whoahqa.models import (
    User,
    ReportingPeriod
)
from whoahqa.views.helpers import get_period_from_request


@view_defaults(route_name='users')
class UserViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='clinics',
                 renderer='clinics_summary.jinja2',
                 permission=perms.CAN_LIST_CLINICS,
                 context=User)
    def clinics(self):
        user = self.request.context
        clinics = user.get_clinics()
        period = get_period_from_request(self.request)

        municipality = user.get_municipality_from_clinics()

        return {
            'period': period,
            'periods': ReportingPeriod.get_active_periods(),
            'municipality': municipality,
            'locations': clinics,
            'key_indicators_key_labels': constants.INDICATOR_LABELS
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
