import unicodedata

from hashids import Hashids
from pyenketo import Enketo
from babel.dates import format_date

from pyramid.i18n import TranslationStringFactory, get_localizer


translation_string_factory = TranslationStringFactory('who-ahqa')
hashid = Hashids(min_length=4, alphabet='abcdefghijklmnpqrstuvwxyz123456789')
enketo = Enketo()


def tuple_to_dict_list(key_tuple, value_tuples):
    return [dict(zip(key_tuple, c)) for c in value_tuples]


def format_date_for_locale(value, format_def, request):
    localizer = get_localizer(request)
    return format_date(value, format_def, locale=localizer.locale_name)


def format_location_name(value):
    return '' if value is None else value.replace("_", " ").title()


def filter_dict_list_by_attr(
        active_ids, characteristic_list, attribute, invert=False):
    return [c for c in characteristic_list
            if (c.get(attribute) in active_ids) != invert]


def check_meets_threshold(num_responses, recommended_sample_frame, ratio):
    return num_responses >= round(recommended_sample_frame * ratio)


def round_or_none(value):
    if value:
        return round(value, 2)
    else:
        return 0


def normalizeString(row):
    normalized_row = unicodedata.normalize('NFD', row)\
        .encode('ascii', 'ignore').lower().replace(' ', '_')
    return normalized_row
