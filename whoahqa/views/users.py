import uuid

from pyramid.view import (
    view_config,
    view_defaults,
)
from pyenketo import Enketo

from whoahqa import constants
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
        # get enketo edit url
        enketo = Enketo()
        enketo.configure(
            self.request.registry.settings['enketo_url'],
            self.request.registry.settings['enketo_api_token'])
        xml_instance = '<?xml version=\'1.0\' ?><clinic_registration id=\"clinic_registration\"><formhub><uuid>73242968f5754dc49c38463af658f3d2</uuid></formhub><user_id>{}</user_id><clinic_name></clinic_name><meta><instanceID>uuid:ec5ce15e-5a0a-4246-93fe-acf60ef69bf2</instanceID></meta></clinic_registration>'.format(self.request.ona_user.user_id)
        edit_url = enketo.get_edit_url(
            self.request.registry.settings['form_server_url'],
            constants.CLINIC_REGISTRATION,
            xml_instance,
            uuid.uuid4(),
            self.request.route_url(
                'users', traverse=(self.request.ona_user.user_id, 'clinics'))
            )
        return {
            'clinics': clinics,
            'edit_url': edit_url
        }
