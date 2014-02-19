import json
from pyramid.security import (
    remember,
    forget,
    NO_PERMISSION_REQUIRED,
)
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
)
from pyramid.view import (
    view_config,
)

from requests_oauthlib import OAuth2Session

from whoahqa.models import (
    DBSession,
    OnaUser,
)


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
        ona_user = OnaUser.get_or_create_from_api_data(
            user_data, refresh_token)
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
