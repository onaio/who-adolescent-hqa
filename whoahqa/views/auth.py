import json
from pyramid.security import (
    remember,
    forget,
    NO_PERMISSION_REQUIRED,
)
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
    HTTPBadRequest,
)
from pyramid.view import (
    view_config,
    forbidden_view_config,
    render_view,
)
from pyramid.response import Response
from requests_oauthlib import OAuth2Session
from sqlalchemy.orm.exc import NoResultFound
from whoahqa.models import (
    DBSession,
    UserProfile,
    OnaUser,
)


def check_post_csrf(func):
    def inner(context, request):
        if request.method == "POST":
            if request.session.get_csrf_token()\
                    != request.POST.get('csrf_token'):
                return HTTPBadRequest("Bad csrf token")
        # fall through if not POST or token is valid
        return func.__call__(context, request)
    return inner


@forbidden_view_config()
def forbidden(context, request):
    # if not authenticated, show login screen with unauthorized status code
    if not request.user:
        return Response(
            render_view(
                context, request, 'login', secure=False), status=401)
    # otherwise, raise HTTPForbidden
    return HTTPForbidden()


@view_config(route_name='auth',
             match_param='action=login',
             permission=NO_PERMISSION_REQUIRED,
             renderer='login.jinja2')
@view_config(name='login',
             context=HTTPForbidden,
             permission=NO_PERMISSION_REQUIRED,
             renderer='password_login.jinja2',
             decorator=check_post_csrf)
def login(request):
    return {}


@view_config(route_name='auth',
             match_param='action=sign-in',
             permission=NO_PERMISSION_REQUIRED,
             renderer='password_login.jinja2',
             decorator=check_post_csrf)
def password_login(context, request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user_profile = UserProfile.get(UserProfile.username == username)
        except NoResultFound:
            pass
        else:
            if user_profile.check_password(password):
                headers = remember(request, user_profile.user_id)
                return HTTPFound(request.route_url('default'), headers=headers)

        # we're still here set the error message
        request.session.flash(
            u"Invalid username or password", 'error')

    return {}


@view_config(
    route_name='logout',
    permission=NO_PERMISSION_REQUIRED)
def logout(request):
    headers = forget(request)
    if request.user.ona_user is None:
        return HTTPFound(
            request.route_url('auth', action='sign-in'), headers=headers)

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
    try:
        user_data = json.loads(response.text)
    except ValueError:
        # couldn't decode json
        pass
    else:
        refresh_token = token['refresh_token']
        try:
            ona_user = OnaUser.get_or_create_from_api_data(
                user_data, refresh_token)
        except ValueError:
            pass
        else:
            request.session['oauth_token'] = json.dumps(token)
            # flash to get the auto-inc id
            DBSession.flush()
            user_id = ona_user.user.id

            # login user
            headers = remember(request, user_id)

            # TODO: redirect to `came_from` url
            return HTTPFound(request.route_url('default'), headers=headers)

    request.session.flash(
        u"Failed to login, please try again", 'error')
    return HTTPFound(
        request.route_url('auth', action='login'))
