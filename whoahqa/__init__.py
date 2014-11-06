import datetime
import logging.config
import transaction

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config

from whoahqa.constants import permissions as perms
from utils import hashid, enketo, format_date_for_locale
from whoahqa.security import group_finder, pwd_context
from whoahqa.models import (
    DBSession,
    Base,
    Clinic,
    Group,
    OnaUser,
    User,
    UserProfile,
    UserFactory,
    ClinicFactory,
    SubmissionFactory,
    ReportingPeriod,
    ReportingPeriodFactory,
)
from whoahqa.views import (
    get_request_user,
    can_list_clinics
)

DEVELOPMENT_ENV = "development"


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

    # add locale directory to project configuration
    config.add_translation_dirs('whoahqa:locale')

    # configure enketo
    enketo.configure(
        settings['enketo_url'],
        settings['enketo_api_token'])

    logging.config.fileConfig(
        global_config['__file__'], disable_existing_loggers=False)

    # configure password context
    pwd_context.load_path(global_config['__file__'])

    includeme(config)

    if settings.get("environment", "") == DEVELOPMENT_ENV:
        setup_development_data()

    return config.make_wsgi_app()


def includeme(config):
    config.include('pyramid_jinja2')
    config.commit()

    config.add_jinja2_search_path("whoahqa:templates")
    config.get_jinja2_environment().filters['format_date'] = \
        format_date_for_locale
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('default', '/')
    config.add_route('locale', '/locale/')
    config.add_route('auth', '/auth/{action}')
    config.add_route('users', '/users/*traverse',
                     factory=UserFactory)
    config.add_route('clinics', '/clinics/*traverse',
                     factory=ClinicFactory)
    config.add_route('submissions', '/submissions/*traverse',
                     factory=SubmissionFactory)
    config.add_route('periods', '/reporting-periods/*traverse',
                     factory=ReportingPeriodFactory)
    config.scan()


def setup_development_data():
    with transaction.manager:
        setup_users()
        setup_clinics()
        setup_default_reporting_period()


def setup_users():
    group_criteria = Group.name == 'su'
    group_params = {'name': 'su'}
    su_group = Group.get_or_create(
        group_criteria,
        **group_params)

    su = User()
    user_profile_criteria = UserProfile.username == 'admin'
    user_profile_params = {
        'user': su,
        'username': 'admin',
        'password': 'admin'}

    profile = UserProfile.get_or_create(
        user_profile_criteria,
        **user_profile_params)

    ona_user_params = {
        'user': su,
        'username': 'admin',
        'refresh_token': '123456'}
    ona_user = OnaUser.get_or_create(
        OnaUser.username == "admin",
        **ona_user_params)

    su.groups.append(su_group)
    profile.save()
    ona_user.save()


def setup_clinics():
    # add a couple of clinics
    clinic_criteria = Clinic.name == "Clinic A"
    clinic_params = {
        "name": "Clinic A",
        "code": "1A2B"}
    clinic = Clinic.get_or_create(
        clinic_criteria,
        **clinic_params)
    clinic.save()
    user = OnaUser.get(OnaUser.username == 'admin').user
    clinic.assign_to(user)


def setup_default_reporting_period():
    title = 'Dev Period'
    params = {
        "title": title,
        "start_date": datetime.datetime(2014, 11, 5),
        "end_date": datetime.datetime(2014, 11, 30)
    }
    reporting_period = ReportingPeriod.get_or_create(
        ReportingPeriod.title == title,
        **params)

    reporting_period.save()
