from pyramid.httpexceptions import HTTPFound

from whoahqa.constants import characteristics as constants
from whoahqa.constants import permissions as perms
from whoahqa.constants import groups
from pyramid.view import view_config


@view_config(route_name='default')
def default(request):
    ona_user = request.ona_user

    user_setting = ona_user.user.settings
    if user_setting:
        request.response.set_cookie(
            '_LOCALE_', user_setting.language)

    url = request.route_url('clinics', traverse=())

    # redirect to view depending on the group which user belongs

    if ona_user.location:
        if ona_user.group and ona_user.group.name == groups.STATE_OFFICIAL:
            url = request.route_url('states', traverse=(ona_user.location.id))
        elif ona_user.group.name == groups.MUNICIPALITY_MANAGER:
            url = request.route_url(
                'municipalities', traverse=(ona_user.location.id))

    return HTTPFound(url)


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
