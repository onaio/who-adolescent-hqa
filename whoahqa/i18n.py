from pyramid.i18n import (
    get_localizer, 
    TranslationStringFactory as _
)


def add_renderer_globals(event):
    request = event.get('request')
    if request is None:
        request = get_current_request()
    event['_'] = request.translate
    event['localizer'] = request.localizer


def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)

    def auto_translate(string):
        return localizer.translate(tsf(string))
    request.localizer = localizer
    request.translate = auto_translate