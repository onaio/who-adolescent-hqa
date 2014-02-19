from pyramid.view import (
    view_config,
    view_defaults,
)

from whoahqa.constants import permissions as perms
from whoahqa.models import (
    User,
)


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
        return {
            'clinics': clinics
        }
