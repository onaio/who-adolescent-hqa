from pyramid.security import authenticated_userid
from pyramid.response import Response
from pyramid.view import (
    view_config,
    view_defaults,
)

from sqlalchemy.exc import DBAPIError

from whoahqa.models import (
    DBSession,
    Clinic,
    ClinicFactory
)



@view_config(route_name='users', renderer='templates/user_clinics.jinja2',
             name='clinics')
def users_clinics(request):
    user = request.context
    clinics = user.get_clinics()
    return {
        'clinics': clinics
    }

@view_defaults(route_name='clinics')
class ClinicViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(renderer='templates/unassigned_clinics.jinja2',
                 name='unassigned')
    def unassigned(self):
        clinics = ClinicFactory.get_unassigned_clinics()
        return {
            'clinics': clinics
        }

    @view_config(name='assign', request_method='POST', check_csrf=True)
    def assign(self):
        clinic = self.request.context
        user = self.request.user
        clinic.assign_to(user)