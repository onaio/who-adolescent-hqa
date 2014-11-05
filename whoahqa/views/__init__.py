from pyramid.httpexceptions import (
    HTTPFound,
)

from pyramid.view import view_config  # noqa

from request_methods import get_request_user, can_list_clinics  # noqa
from auth import oauth_authorize, oauth_callback  # noqa
from clinics import ClinicViews  # noqa
from users import UserViews  # noqa
from submissions import SubmissionViews  # noqa


@view_config(route_name='default')
def default(request):
    ona_user = request.ona_user

    return HTTPFound(
        request.route_url(
            'users',
            traverse=(ona_user.user.id, 'select-period'),
            _query={
                'came_from': request.route_path(
                    'users',
                    traverse=(ona_user.user.id, '{period_id}', 'clinics'))}))
