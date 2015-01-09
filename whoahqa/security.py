from sqlalchemy.orm.exc import NoResultFound
from passlib.context import CryptContext
from pyramid.security import Authenticated

from whoahqa.constants import permissions, groups


pwd_context = CryptContext()


GROUPS = [groups.MUNICIPALITY_MANAGER]


GROUP_PERMISSIONS = {
    groups.MUNICIPALITY_MANAGER: [permissions.CAN_LIST_CLINICS,
                                  permissions.CAN_VIEW_CLINICS,
                                  permissions.CAN_EDIT_CLINICS,
                                  permissions.CAN_ASSESS_CLINICS,
                                  permissions.CAN_VIEW_MUNICIPALITY],
    groups.USER: [Authenticated],
    groups.SUPER_USER: [permissions.SUPER_USER]
}


def group_finder(userid, request):
    from whoahqa.models import User
    try:
        user = User.get(User.id == userid)
    except NoResultFound:
        return None
    else:
        principals = []
        if user.group:
            principals = GROUP_PERMISSIONS.get(user.group.name, [])

        principals.append("u:{}".format(userid))
        return principals
