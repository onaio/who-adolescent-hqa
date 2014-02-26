import uuid

from pyramid.view import (
    view_config
)
from pyramid.httpexceptions import (
    HTTPFound
)
from pyenketo import Enketo
from whoahqa import constants
from whoahqa.constants import permissions as perms

@view_config(name='register',
             route_name='register',
             permission=perms.AUTHENTICATED
            )
def register_clinic(request):
    # get enketo edit url
    enketo = Enketo()
    enketo.configure(
        request.registry.settings['enketo_url'],
        request.registry.settings['enketo_api_token'])
    xml_instance = '<?xml version=\'1.0\' ?><clinic_registration id=\"clinic_registration\"><formhub><uuid>73242968f5754dc49c38463af658f3d2</uuid></formhub><user_id>{}</user_id><clinic_name></clinic_name><meta><instanceID>uuid:ec5ce15e-5a0a-4246-93fe-acf60ef69bf2</instanceID></meta></clinic_registration>'.format(
        request.ona_user.user_id)
    edit_url = enketo.get_edit_url(
        request.registry.settings['form_server_url'],
        constants.CLINIC_REGISTRATION,
        xml_instance,
        uuid.uuid4(),
        request.route_url(
            'users', traverse=(request.ona_user.user_id, 'clinics'))
    )

    return HTTPFound(location=edit_url)
