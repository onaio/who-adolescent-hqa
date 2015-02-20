from sqlalchemy.orm.exc import NoResultFound
from passlib.context import CryptContext
from pyramid.security import (
    Authenticated)

from whoahqa.constants import permissions, groups


pwd_context = CryptContext()


GROUPS = [groups.MUNICIPALITY_MANAGER]


GROUP_PERMISSIONS = {
    groups.MUNICIPALITY_MANAGER: [permissions.CAN_CREATE_PERIOD,
                                  permissions.CAN_LIST_CLINICS,
                                  permissions.CAN_VIEW_CLINICS,
                                  permissions.CAN_EDIT_CLINICS,
                                  permissions.CAN_ASSESS_CLINICS,
                                  permissions.CAN_LIST_MUNICIPALITY,
                                  permissions.CAN_VIEW_MUNICIPALITY],
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
