import uuid

from pyramid.view import (
    view_config,
    view_defaults,
)

from whoahqa import constants
from whoahqa.constants import permissions as perms
from whoahqa.models import (
    User,
)
from whoahqa.utils import tuple_to_dict_list


@view_defaults(route_name='users')
class UserViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='clinics',
                 renderer='user_clinics.jinja2',
                 permission=perms.LIST_USER_CLINICS,
                 context=User)
    def clinics(self):
        user = self.request.context
        clinics = user.get_clinics()
        characteristics = tuple_to_dict_list(("id", "description"), constants.CHARACTERISTICS)
        key_indicators = [i for i,v in constants.KEY_INDICATORS]
        clinic_scores = {}
        for clinic in clinics:
            scores = clinic.get_scores()
            clinic_scores[clinic.id] = scores
        return {
            'clinics': clinics,
            'characteristics': characteristics,
            'clinic_scores': clinic_scores,
            'score_limits': constants.SCORE_RANGE_LIMITS,
            'key_indicators': key_indicators
        }
