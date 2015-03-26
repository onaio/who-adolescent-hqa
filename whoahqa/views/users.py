from pyramid.httpexceptions import HTTPFound
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


@view_defaults(route_name='users')
class UserViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='clinics',
                 renderer='clinics_summary.jinja2',
                 permission=perms.CAN_LIST_CLINICS,
                 context=ReportingPeriod)
    def clinics(self):
        period = self.request.context
        user = period.__parent__
        clinics = user.get_clinics()

        return {
            'period': period,
            'locations': clinics,
            'key_indicators_key_labels': constants.INDICATOR_LABELS
        }

    @view_config(name='clinics',
                 permission=perms.CAN_VIEW_CLINICS,
                 context=User)
    def reporting_period_redirect(self):
        user = self.request.context
        return HTTPFound(
            self.request.route_url(
                'users',
                traverse=(user.id, 'select-period'),
                _query={
                    'came_from': self.request.route_path(
                        'users', traverse=(user.id, '{period_id}', 'clinics'))
                }))

    @view_config(name='select-period',
                 renderer='reporting_period_select.jinja2',
                 permission=perms.AUTHENTICATED,
                 context=User)
    def select_reporting_period(self):
        user = self.request.context
        periods = ReportingPeriod.all()
        url_target = self.request.GET.get('came_from')
        return {'periods': periods, 'user': user, 'url_target': url_target}
