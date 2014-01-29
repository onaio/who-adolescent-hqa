from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from whoahqa.models import (
    DBSession,
    Clinic,
    ClinicFactory
)


@view_config(route_name='clinics', renderer='templates/unassigned_clinics.pt',
             name='unassigned')
def unassigned_clinics(request):
    clinics = ClinicFactory.get_unassigned_clinics()
    return {
        'clinics': clinics
    }


@view_config(route_name='users', renderer='templates/user_clinics.pt',
             name='clinics')
def user_clinics(request):
    clinics = ClinicFactory.get_user_clinics(request.context)
    return {
        'clinics': clinics
    }