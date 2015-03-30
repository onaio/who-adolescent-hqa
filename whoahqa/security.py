from sqlalchemy.orm.exc import NoResultFound
from passlib.context import CryptContext
from pyramid.security import (
    Authenticated)

from whoahqa.constants import permissions as perms, groups


pwd_context = CryptContext()


GROUPS = [groups.MUNICIPALITY_MANAGER]

CLINIC_MANAGER_PERMS = [perms.CAN_LIST_CLINICS,
                        perms.CAN_VIEW_CLINICS,
                        perms.CAN_EDIT_CLINICS]

MUNICIPALITY_MANAGER_PERMS = [perms.CAN_CREATE_PERIOD,
                              perms.CAN_ASSESS_CLINICS,
                              perms.CAN_VIEW_MUNICIPALITY] + \
    CLINIC_MANAGER_PERMS

STATE_OFFICIAL_PERMS = MUNICIPALITY_MANAGER_PERMS + (
    [perms.CAN_LIST_MUNICIPALITY,
     perms.CAN_LIST_STATE,
     perms.CAN_VIEW_STATE])

GROUP_PERMISSIONS = {
    groups.MUNICIPALITY_MANAGER: MUNICIPALITY_MANAGER_PERMS,
    groups.STATE_OFFICIAL: STATE_OFFICIAL_PERMS,
    groups.USER: [Authenticated],
    groups.SUPER_USER: []
}


def group_finder(userid, request):
    from whoahqa.models import User

    principals = []
    principals.append("u:{}".format(userid))
    try:
        user = User.get(User.id == userid)
    except NoResultFound:
        return None
    else:
        if user.group:
            principals.append(user.group.name)
            principals.extend(GROUP_PERMISSIONS.get(user.group.name, []))

        return principals
