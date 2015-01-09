from sqlalchemy.orm.exc import NoResultFound
from passlib.context import CryptContext

from whoahqa.constants import permissions, groups


pwd_context = CryptContext()


GROUPS = [groups.MUNICIPALITY_MANAGER]


GROUP_PERMISSIONS = {
    groups.MUNICIPALITY_MANAGER: [permissions.CAN_LIST_CLINICS,
                                  permissions.CAN_VIEW_CLINICS,
                                  permissions.CAN_EDIT_CLINICS,
                                  permissions.CAN_ASSESS_CLINICS,
                                  permissions.CAN_VIEW_MUNICIPALITY]
}


def group_finder(userid, request):
    from whoahqa.models import User
    try:
        user = User.get(User.id == userid)
    except NoResultFound:
        return None
    else:
        principals = []
        if user.group == groups.SUPER_USER:
            principals.append(user.group)
        else:
            principals = GROUP_PERMISSIONS.get(user.group, [])

        principals.append("u:{}".format(userid))
        return principals
