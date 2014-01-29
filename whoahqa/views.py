from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from whoahqa.models import (
    DBSession,
    Clinic,
    ClinicFactory
)


@view_config(
    route_name='clinics', renderer='templates/unassigned_clinics',
    name='un-assigned')
def unassigned_clinics(request):
    clinics = ClinicFactory.get_unassigned_clinics()
    return {
        'clinics': clinics
    }

