from pyramid.httpexceptions import HTTPFound

from whoahqa.constants import characteristics as constants
from whoahqa.constants import permissions as perms

from whoahqa.views.helpers import get_period_from_request

from pyramid.view import view_config


@view_config(route_name='default')
def default(request):
    ona_user = request.ona_user

    period = get_period_from_request(request)

    user_setting = ona_user.user.settings
    if user_setting:
        request.response.set_cookie(
            '_LOCALE_', user_setting.language)

    url = request.route_url('clinics', traverse=(),
                            _query={'period': period.id})

    # redirect to view depending on location owned

    if ona_user.location:
        url = ona_user.location.get_url(request, period)

    return HTTPFound(url)


@view_config(route_name='locale',
             permission=perms.AUTHENTICATED,
             renderer='locale.jinja2')
def set_locale(request):
    ona_user = request.ona_user
    user_settings = ona_user.user.settings

    available_languages = constants.AVAILABLE_LANGUAGES
    period = get_period_from_request(request)

    if request.method == "POST":
        locale = request.POST.get("locale", "")
        if locale and locale in available_languages:
            user_settings.language = locale
            user_settings.save()
            request.response.set_cookie('_LOCALE_', locale)

    return {
        "available_languages": available_languages,
        "period": period,
        "user_settings": user_settings}
