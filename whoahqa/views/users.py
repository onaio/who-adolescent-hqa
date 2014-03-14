import uuid

from pyramid.view import (
    view_config,
    view_defaults,
)

from whoahqa import constants
from whoahqa.constants import permissions as perms
from whoahqa.models import (
    User,
    ReportingPeriod
)
from whoahqa.utils import tuple_to_dict_list


@view_defaults(route_name='users')
class UserViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='clinics',
                 renderer='user_clinics.jinja2',
                 permission=perms.LIST_USER_CLINICS,
                 context=ReportingPeriod)
    def clinics(self):
        period = self.request.context
        user = period.__parent__
        clinics = user.get_clinics()

        key_indicators = [i for i, v in constants.KEY_INDICATORS]
        key_indicator_char_map = tuple_to_dict_list(
            ("id", "characteristics"), constants.KEY_INDICATORS)
        return {
            'period': period,
            'clinics': clinics,
            'key_indicators': key_indicators,
            'key_indicator_char_map': key_indicator_char_map
        }

    @view_config(name='summary',
                 renderer='clinics_score_summary.jinja2',
                 permission=perms.LIST_USER_CLINICS,
                 context=User)
    def clinics_score_summary(self):
        user = self.request.context
        clinics = user.get_clinics()
        characteristics = tuple_to_dict_list(
            ("id", "description"), constants.CHARACTERISTICS)
        clinic_scores = {}
        for clinic in clinics:
            scores = clinic.get_scores()
            clinic_scores[clinic.id] = scores
        return {
            'clinics': clinics,
            'characteristics': characteristics,
            'clinic_scores': clinic_scores,
            'score_limits': constants.SCORE_RANGE_LIMITS,
        }

    @view_config(name='select-period',
                 renderer='reporting_period_select.jinja2',
                 permission=perms.LIST_USER_CLINICS,
                 context=User)
    def select_reporting_period(self):
        user = self.request.context
        periods = ReportingPeriod.all()
        return {'periods': periods, 'user':user}
