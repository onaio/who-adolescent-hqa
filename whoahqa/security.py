from sqlalchemy.orm.exc import NoResultFound
from passlib.context import CryptContext


pwd_context = CryptContext()


def group_finder(userid, request):
    from whoahqa.models import User
    try:
        user = User.get(User.id == userid)
    except NoResultFound:
        return None
    else:
        groups = ["g:{}".format(g.name) for g in user.groups]
        groups.append("u:{}".format(userid))
        return groups
