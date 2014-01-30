from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy import engine_from_config

from whoahqa.security import group_finder
from whoahqa.models import (
    DBSession,
    Base,
    UserFactory,
    ClinicFactory
)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings,
                          root_factory='whoahqa.models.RootFactory')
    config.set_authentication_policy(
        AuthTktAuthenticationPolicy(settings['auth_key'],
                                    callback=group_finder,
                                    hashalg='sha512'))
    config.set_authorization_policy(ACLAuthorizationPolicy())
    includeme(config)
    return config.make_wsgi_app()


def includeme(config):
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('users', '/users/*traverse',
                     factory=UserFactory)
    config.add_route('clinics', '/clinics/*traverse',
                     factory=ClinicFactory)
    config.scan()
