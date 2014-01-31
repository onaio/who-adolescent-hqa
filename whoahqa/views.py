from pyramid.security import authenticated_userid
from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )
from pyramid.view import (
    view_config,
    view_defaults,
)
from pyramid.events import NewRequest
from pyramid.events import subscriber

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import NoResultFound

from whoahqa.models import (
    DBSession,
    ClinicFactory,
    User,
    Clinic
)

@subscriber(NewRequest)
def set_request_user(event):
    request = event.request
    user_id = authenticated_userid(request)
    try:
        request.user = User.get(User.id == user_id)
    except NoResultFound:
        request.user = None


@view_defaults(route_name='users')
class UserViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(renderer='templates/user_clinics.jinja2', name='clinics')
    def clinics(self):
        user = self.request.context
        clinics = user.get_clinics()
        return {
            'clinics': clinics
        }


@view_defaults(route_name='clinics')
class ClinicViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(renderer='templates/clinics_unassigned.jinja2',
                 name='unassigned')
    def unassigned(self):
        clinics = Clinic.get_unassigned()
        return {
            'clinics': clinics
        }

    @view_config(name='assign', request_method='POST', check_csrf=False)
    def assign(self):
        user = self.request.user

        # get the list of requested clinics
        clinic_ids = self.request.POST.getall('clinic_id')
        clinics = Clinic.all(Clinic.id.in_(clinic_ids))
        for clinic in clinics:
            clinic.assign_to(user)
        return HTTPFound(
            self.request.route_url('clinics', traverse=('unassigned',)))

    @view_config(name='', request_method='GET', context=Clinic,
                 renderer='templates/clinics_show.jinja2')
    def show(self):
        clinic = self.request.context
        return {
            'clinic': clinic
        }