from pyramid.httpexceptions import (
    HTTPFound,
)

from pyramid.view import (
    view_config,
)

from request_methods import (
    get_request_user,
    can_list_clinics,)
from auth import (
    oauth_authorize,
    oauth_callback,)
from clinics import ClinicViews
from users import UserViews
from submissions import SubmissionViews


@view_config(route_name='default')
def default(request):
    return HTTPFound(request.route_url('clinics', traverse=()))
