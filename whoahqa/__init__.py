from pyramid.config import Configurator
from sqlalchemy import engine_from_config

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
    config = Configurator(settings=settings)
    includeme(config)
    return config.make_wsgi_app()


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('user_clinics', '/clinics/user/*traverse',
                     factory=UserFactory)
    config.add_route('clinics', '/clinics/*traverse',
                     factory=ClinicFactory)
    config.scan()
