import csv
import codecs
import unicodedata

from collections import Counter
from hashids import Hashids
from pyenketo import Enketo
from babel.dates import format_date
from whoahqa.constants import characteristics
from pyramid.i18n import TranslationStringFactory, get_localizer

translation_string_factory = TranslationStringFactory('who-ahqa')
hashid = Hashids(min_length=4, alphabet='abcdefghijklmnpqrstuvwxyz123456789')
enketo = Enketo()

INITIAL_SCORE_MAP = {characteristics.EQUITABLE: 0,
                     characteristics.ACCESSIBLE: 0,
                     characteristics.ACCEPTABLE: 0,
                     characteristics.APPROPRIATE: 0,
                     characteristics.EFFECTIVE: 0}


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


def valid_year(year):
    if year and year.isdigit() and int(year) >= 1900 and int(year) <= 2099:
            return int(year)


def clinics_report(clinics, period):
    results = reduce(lambda x, y: Counter(x) + Counter(y),
                     (c.key_indicators(period) for c in clinics),
                     INITIAL_SCORE_MAP)
    return results


class UnicodeDictReader(object):
    def __init__(self, *args, **kw):
        self.encoding = kw.pop('encoding', 'utf-8')
        self.reader = csv.DictReader(*args, **kw)

    def __iter__(self):
        decode = codecs.getdecoder(self.encoding)
        for row in self.reader:
            t = dict((k, decode(row[k])[0]) for k in row)
            yield t
