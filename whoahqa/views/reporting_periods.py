from pyramid.security import (
    has_permission,
)
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPBadRequest,
)
from pyramid.view import (
    view_config,
    view_defaults,
)

from whoahqa.models import ReportingPeriod
from whoahqa.views.base import BaseClassViews

@view_defaults(route_name='periods')
class ReportingPeriodViews(BaseClassViews):

    @view_config(
        name='', permission='list', renderer='reporting_periods_list.jinja2')
    def list(self):
        periods = ReportingPeriod.all()
        return {'periods': periods}
