from sqlalchemy.orm.exc import NoResultFound

from whoahqa.models import (
    ClinicFactory,
    OnaUser,
)

from whoahqa.constants import groups
from whoahqa.constants import permissions as perms


def get_request_user(request):
    user_id = request.authenticated_userid
    try:
        return OnaUser.get(OnaUser.user_id == user_id)
    except NoResultFound:
        return None


def can_list_clinics(request):
    return request.has_permission(perms.CAN_LIST_CLINICS,
                                  ClinicFactory(request))


def can_view_clinics(request):
    return request.has_permission(perms.CAN_VIEW_CLINICS,
                                  ClinicFactory(request))


def is_super_user(request):
    return request.has_permission(perms.SUPER_USER,
                                  ClinicFactory(request))


def can_access_clinics(request):
    return request.has_permission(perms.CAN_ASSESS_CLINICS,
                                  ClinicFactory(request))


def can_view_municipality(request):
    ona_user = request.ona_user
    if ona_user.user.group.name == groups.MUNICIPALITY_MANAGER or (
            ona_user.user.group.name == groups.STATE_OFFICIAL):
        return True

    return False


def can_view_state(request):
    ona_user = request.ona_user
    if ona_user.user.group.name == groups.STATE_OFFICIAL:
        return True

    return False
