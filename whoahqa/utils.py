from hashids import Hashids
from pyenketo import Enketo
from babel.dates import format_date

from pyramid.i18n import TranslationStringFactory, get_localizer


translation_string_factory = TranslationStringFactory('who-ahqa')
hashid = Hashids(min_length=4, alphabet='abcdefghijklmnpqrstuvwxyz123456789')
enketo = Enketo()


def tuple_to_dict_list(key_tuple, value_tuples):
    return [dict(zip(key_tuple, c)) for c in value_tuples]


def format_locale_date(value, format_def, request):
    localizer = get_localizer(request)
    return format_date(value, format_def, locale=localizer.locale_name)
