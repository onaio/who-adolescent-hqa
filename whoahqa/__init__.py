import logging.config

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config

from whoahqa.constants import permissions as perms
from utils import hashid, enketo
from whoahqa.security import group_finder, pwd_context
from whoahqa.models import (
    DBSession,
    Base,
    UserFactory,
    ClinicFactory,
    SubmissionFactory
)
from whoahqa.views import (
    get_request_user,
    can_list_clinics
)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    session_factory = UnencryptedCookieSessionFactoryConfig(
        settings['secret_key'])
    config = Configurator(settings=settings,
                          root_factory='whoahqa.models.RootFactory',
                          session_factory=session_factory)
    config.set_authentication_policy(
        AuthTktAuthenticationPolicy(settings['secret_key'],
                                    callback=group_finder,
                                    hashalg='sha512'))

    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_default_permission(perms.AUTHENTICATED)

    # add .user to requests and cache it with reify
    config.add_request_method(get_request_user, 'ona_user', reify=True)
    config.add_request_method(can_list_clinics, 'can_list_clinics', reify=True)

    # setup the hashid salt
    hashid._salt = settings['hashid_salt']

    # configure enketo
    enketo.configure(
        settings['enketo_url'],
        settings['enketo_api_token'])

    logging.config.fileConfig(
        global_config['__file__'], disable_existing_loggers=False)

    # configure password context
    pwd_context.load_path(global_config['__file__'])

    includeme(config)
    return config.make_wsgi_app()


def includeme(config):
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("whoahqa:templates")
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('default', '/')
    config.add_route('auth', '/auth/{action}')
    config.add_route('users', '/users/*traverse',
                     factory=UserFactory)
    config.add_route('clinics', '/clinics/*traverse',
                     factory=ClinicFactory)
    config.add_route('submissions', '/submissions/*traverse',
                     factory=SubmissionFactory)
    config.scan()
