import json
from pyramid.security import (
    authenticated_userid,
    remember,
    forget,
    NO_PERMISSION_REQUIRED,
    has_permission,
)
from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPBadRequest,
    HTTPUnauthorized,
    HTTPForbidden,
)
from pyramid.view import (
    view_config,
    view_defaults,
    forbidden_view_config,
    render_view
)


from sqlalchemy.orm.exc import NoResultFound

from requests_oauthlib import OAuth2Session

from whoahqa import constants
from whoahqa.constants import permissions as perms
from whoahqa.utils import tuple_to_dict_list
from whoahqa.models import (
    DBSession,
    ClinicFactory,
    SubmissionFactory,
    User,
    OnaUser,
    Clinic,
    Submission,
    ClinicNotFound,
)


def get_request_user(request):
    user_id = authenticated_userid(request)
    try:
        return User.get(User.id == user_id)
    except NoResultFound:
        return None


def can_list_clinics(request):
    return has_permission('list', ClinicFactory(request), request)


@forbidden_view_config()
def forbidden(context, request):
    # if not authenticated, show login screen
    if not request.user:
        return Response(render_view(context, request, 'login', secure=False))
    # otherwise, raise HTTPUnauthorized
    return HTTPForbidden()


@view_config(
    route_name='default',
    renderer='login.jinja2')
def default(request):
    return HTTPFound(request.route_url('clinics', traverse=()))


@view_config(route_name='auth',
             match_param='action=login',
             permission=NO_PERMISSION_REQUIRED,
             renderer='login.jinja2')
@view_config(name='login',
             context=HTTPForbidden,
             permission=NO_PERMISSION_REQUIRED,
             renderer='login.jinja2')
def login(request):
    return {}


@view_config(
    route_name='auth',
    match_param='action=logout',
    permission=NO_PERMISSION_REQUIRED)
def logout(request):
    headers = forget(request)
    return HTTPFound(
        request.route_url('auth', action='login'), headers=headers)


@view_config(
    route_name='auth',
    match_param='action=authorize',
    permission=NO_PERMISSION_REQUIRED)
def oauth_authorize(request):
    client_id = request.registry.settings['oauth_client_id']
    authorization_endpoint = "{base_url}{path}".format(
        base_url=request.registry.settings['oauth_base_url'],
        path=request.registry.settings['oauth_authorization_path'])
    redirect_uri = request.route_url('auth', action='callback')

    session = OAuth2Session(
        client_id,
        scope=['read', 'groups'],
        redirect_uri=redirect_uri)
    authorization_url, state = session.authorization_url(
        authorization_endpoint)
    # State is used to prevent CSRF, keep this for later.
    request.session['oauth_state'] = state
    return HTTPFound(authorization_url)


@view_config(
    route_name='auth',
    match_param='action=callback',
    permission=NO_PERMISSION_REQUIRED)
def oauth_callback(request):
    # check if we have `error` in our params, meaning user canceled
    if 'error' in request.GET:
        # redirect to login page with an alert
        request.session.flash(
            u"You must select authorize to continue", 'error')
        return HTTPFound(request.route_url('auth', action='login'))

    # TODO: validate the `oauth_state` session
    base_url = request.registry.settings['oauth_base_url']
    state = request.GET.get('state')
    client_id = request.registry.settings['oauth_client_id']
    client_secret = request.registry.settings['oauth_secret']
    token_url = "{base_url}{path}".format(
        base_url=base_url,
        path=request.registry.settings['oauth_token_path'])
    redirect_uri = request.route_url('auth', action='callback')

    session = OAuth2Session(
        client_id,
        state=state,
        redirect_uri=redirect_uri)
    code = request.GET.get('code')
    token = session.fetch_token(
        token_url,
        client_secret=client_secret,
        code=code)

    # retrieve username and store in db if it doesnt exist yet
    user_api_url = "{base_url}{path}".format(
        base_url=base_url,
        path=request.registry.settings['oauth_user_api_path'])
    response = session.request('GET', user_api_url)
    user_data = json.loads(response.text)
    refresh_token = token['refresh_token']

    try:
        ona_user = OnaUser.get_or_create_from_api_data(user_data, refresh_token)
    except ValueError:
        request.session.flash(
            u"Failed to login, please try again", 'error')
    else:
        request.session['oauth_token'] = json.dumps(token)
        # flash to get the auto-inc id
        DBSession.flush()
        user_id = ona_user.user.id

        # login user
        headers = remember(request, user_id)

        # redirect to `came_from` url
        return HTTPFound(
            request.route_url('users', traverse=(user_id, 'clinics')),
            headers=headers)


@view_defaults(route_name='users')
class UserViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='clinics',
                 renderer='user_clinics.jinja2',
                 permission=perms.LIST_USER_CLINICS,
                 context=User)
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

    @view_config(name='',
                 context=ClinicFactory,
                 renderer='clinics_list.jinja2')
    def list(self):
        # if the user doesnt have permissions to list all clinics,
        #  redirect to his own clinics
        if not has_permission(perms.LIST, self.request.context, self.request):
            return HTTPFound(
                self.request.route_url(
                    'users', traverse=(self.request.user.id, 'clinics')))

        # otherwise, list all clinics
        # TODO: paginate
        return {
            'can_list_clinics': True,
            'clinics': Clinic.all()
        }

    @view_config(name='unassigned',
                 context=ClinicFactory,
                 renderer='clinics_unassigned.jinja2')
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

    @view_config(name='',
                 request_method='GET',
                 context=Clinic,
                 permission=perms.SHOW,
                 renderer='clinics_show.jinja2')
    def show(self):
        clinic = self.request.context

        # if clinic is not assigned, throw a bad request
        if not clinic.is_assigned:
            raise HTTPBadRequest("The clinic is not yet assigned")

        scores = clinic.get_scores()
        return {
            'clinic': clinic,
            'client_tools': tuple_to_dict_list(
                ("id", "name"), constants.CLIENT_TOOLS),
            'characteristics': tuple_to_dict_list(
                ("id", "description"), constants.CHARACTERISTICS),
            'scores': scores
        }


@view_defaults(route_name='submissions')
class SubmissionViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(
        name='',
        request_method='POST',
        context=SubmissionFactory)
    def json_post(self):
        payload = self.request.body
        if not payload:
            return HTTPBadRequest(comment='Missing JSON Payload')

        try:
            Submission.create_from_json(payload)
        except ClinicNotFound:
            return Response('Accepted Pending Clinic Match', status=202)
        else:
            return Response('Saved', status=201)
