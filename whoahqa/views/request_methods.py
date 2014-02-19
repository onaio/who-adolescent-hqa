from pyramid.security import (
    authenticated_userid,
    has_permission,
)

from sqlalchemy.orm.exc import NoResultFound

from whoahqa.models import (
    ClinicFactory,
    User,
)


def get_request_user(request):
    user_id = authenticated_userid(request)
    try:
        return User.get(User.id == user_id)
    except NoResultFound:
        return None


def can_list_clinics(request):
    return has_permission('list', ClinicFactory(request), request)
