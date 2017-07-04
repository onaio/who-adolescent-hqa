from sqlalchemy.orm.exc import NoResultFound

from whoahqa.models import (
    ClinicFactory,
    User,
)

from whoahqa.constants import groups
from whoahqa.constants import permissions as perms


def get_request_user(request):
    user_id = request.authenticated_userid
    try:
        return User.get(User.id == user_id)
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


def can_create_period(request):
    return request.has_permission(perms.CAN_CREATE_PERIOD,
                                  ClinicFactory(request))


def can_view_municipality(request):
    user = request.user
    if user.group.name == groups.MUNICIPALITY_MANAGER or (
            user.group.name == groups.STATE_OFFICIAL):
        return True

    return False


def can_view_state(request):
    user = request.user
    if user.group.name == groups.STATE_OFFICIAL:
        return True

    return False


def can_list_state(request):
    user = request.user
    if user.group.name == groups.NATIONAL_OFFICIAL:
        return True

    return False
