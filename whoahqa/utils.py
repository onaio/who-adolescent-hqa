from hashids import Hashids
from pyenketo import Enketo


hashid = Hashids(min_length=4, alphabet='abcdefghijklmnpqrstuvwxyz123456789')
enketo = Enketo()


def tuple_to_dict_list(key_tuple, value_tuples):
    return [dict(zip(key_tuple, c)) for c in value_tuples]
