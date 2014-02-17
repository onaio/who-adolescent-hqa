from pyramid.security import authenticated_userid
from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPBadRequest,
    )
from pyramid.view import (
    view_config,
    view_defaults,
)
from pyramid.events import NewRequest
from pyramid.events import subscriber

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import NoResultFound

from requests_oauthlib import OAuth2Session

from whoahqa.utils import tuple_to_dict_list
from whoahqa.models import (
    DBSession,
    ClinicFactory,
    SubmissionFactory,
    User,
    Clinic,
    Submission,
    ClinicNotFound,
    CLIENT_TOOLS,
    CHARACTERISTICS,
    CHARACTERISTIC_MAPPING
)

@subscriber(NewRequest)
def set_request_user(event):
    request = event.request
    user_id = authenticated_userid(request)
    try:
        request.user = User.get(User.id == user_id)
    except NoResultFound:
        request.user = None


@view_config(route_name='oauth', match_param='action=login')
def oauth_login(request):
    client_id = request.registry.settings['oauth_client_id']
    authorization_endpoint = "{base_url}{path}".format(
        base_url=request.registry.settings['oauth_base_url'],
        path=request.registry.settings['oauth_authorization_path'])
    redirect_uri = request.route_url('oauth', action='callback')

    session = OAuth2Session(
        client_id,
        scope=['profile', 'email'],
        redirect_uri=redirect_uri)
    authorization_url, state = session.authorization_url(
        authorization_endpoint)
    # State is used to prevent CSRF, keep this for later.
    request.session['oauth_state'] = state
    return HTTPFound(authorization_url)


@view_config(route_name='oauth', match_param='action=callback')
def oauth_callback(request):
    # check if we have `error` in our params, meaning user canceled
    if 'error' in request.GET:
        # redirect to login page with an alert
        request.session.flash(
            u"You must accept the permissions to login", 'error')
        return HTTPFound(request.route_url('oauth', action='login'))

    # TODO: validate the `oauth_state` session
    client_id = request.registry.settings['oauth_client_id']
    client_secret = request.registry.settings['oauth_secret']
    token_url = "{base_url}{path}".format(
        base_url=request.registry.settings['oauth_base_url'],
        path=request.registry.settings['oauth_token_path'])
    redirect_uri = request.route_url('oauth', action='callback')

    session = OAuth2Session(
        client_id,
        state=request.GET.get('state'),
        redirect_uri=redirect_uri)
    code = request.GET.get('code')
    access_token = session.fetch_token(
        token_url,
        client_secret=client_secret,
        code=code)

    # retrieve username and store in db if it doesnt exist yet

    request.session['oauth_token'] = access_token
    # redirect to `from` url
    return HTTPFound(request.route_url('users', traverse=('1', 'clinics')))


@view_defaults(route_name='users')
class UserViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='clinics',
                 renderer='user_clinics.jinja2')
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

    @view_config(name='unassigned',
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

    @view_config(name='', request_method='GET', context=Clinic,
                 renderer='clinics_show.jinja2')
    def show(self):
        clinic = self.request.context

        # if clinic is not assigned, throw a bad request
        if not clinic.is_assigned:
            raise HTTPBadRequest("The clinic is not yet assigned")

        scores = clinic.get_scores()
        return {
            'clinic': clinic,
            'client_tools': tuple_to_dict_list(("id", "name"), CLIENT_TOOLS),
            'characteristics': tuple_to_dict_list(
                ("id", "description"), CHARACTERISTICS),
            'scores': scores
        }


@view_defaults(route_name='submissions')
class SubmissionViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='', request_method='POST', context=SubmissionFactory)
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
