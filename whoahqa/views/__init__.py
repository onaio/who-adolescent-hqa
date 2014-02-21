from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
)
from pyramid.response import Response
from pyramid.view import (
    view_config,
    forbidden_view_config,
    render_view,
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


@forbidden_view_config()
def forbidden(context, request):
    # if not authenticated, show login screen
    if not request.ona_user:
        return Response(
            render_view(context, request, 'login', secure=False), status=401)
    # otherwise, raise HTTPUnauthorized
    return HTTPForbidden()


@view_config(route_name='default')
def default(request):
    return HTTPFound(request.route_url('clinics', traverse=()))
