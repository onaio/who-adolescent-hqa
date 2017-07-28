from pyramid.httpexceptions import HTTPFound

from whoahqa.constants import characteristics as constants
from whoahqa.constants import permissions as perms, groups

from whoahqa.views.helpers import get_period_from_request
from whoahqa.utils import translation_string_factory as _

from pyramid.view import view_config


@view_config(route_name='default')
def default(request):
    user = request.user

    period = get_period_from_request(request)

    user_setting = user.settings
    if user_setting:
        request.response.set_cookie(
            '_LOCALE_', user_setting.language)

    url = request.route_url('clinics', traverse=(),
                            _query={'period': period.id})

    # redirect to view depending on location owned
    group = user.group

    if group and group.name == groups.NATIONAL_OFFICIAL:
        url = request.route_url('states', traverse=(),
                                _query={'period': period.id})

    if user.location:
        url = user.location.get_url(request, period)

    return HTTPFound(url)


@view_config(route_name='locale',
             permission=perms.AUTHENTICATED,
             renderer='locale.jinja2')
def set_locale(request):
    user = request.user
    user_settings = user.settings

    available_languages = constants.AVAILABLE_LANGUAGES
    period = get_period_from_request(request)
    if request.method == "POST":
        locale = request.POST.get("locale", "")
        request._LOCALE_ = locale
        if locale and locale in available_languages:
            user_settings.language = locale
            user_settings.save()
            referrer = request.cookies.get('referrer')
            headers = request.response.headers
            request.response.set_cookie('_LOCALE_', locale)
            request.session.flash(
                _("Language changed successfully"), "success")
            return HTTPFound(
                location=referrer, headers=headers)

    if request.method == "GET":
        referrer = request.referrer
        request.response.set_cookie('referrer', referrer)

    return {
        "available_languages": available_languages,
        "period": period,
        "user_settings": user_settings}
