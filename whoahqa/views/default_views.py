from pyramid.httpexceptions import (
    HTTPFound,
)

from whoahqa.constants import characteristics as constants
from whoahqa.constants import permissions as perms
from pyramid.view import view_config


@view_config(route_name='default')
def default(request):
    ona_user = request.ona_user

    user_setting = ona_user.user.settings
    if user_setting:
        request.response.set_cookie(
            '_LOCALE_', user_setting.language)

    return HTTPFound(request.route_url('clinics', traverse=()))


@view_config(route_name='locale',
             permission=perms.AUTHENTICATED,
             renderer='locale.jinja2')
def set_locale(request):
    ona_user = request.ona_user
    user_settings = ona_user.user.settings

    available_languages = constants.AVAILABLE_LANGUAGES

    if request.method == "POST":
        locale = request.POST.get("locale", "")
        if locale and locale in available_languages:
            user_settings.language = locale
            user_settings.save()
            request.response.set_cookie('_LOCALE_', locale)

    return {
        "available_languages": available_languages,
        "user_settings": user_settings}
