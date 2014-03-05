from pyramid.security import (
    has_permission,
)
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPBadRequest,
)
from pyramid.view import (
    view_config,
    view_defaults,
)

from pyenketo import (
    Enketo,
    Http404,
)

from whoahqa import constants
from whoahqa.constants import permissions as perms
from whoahqa.utils import tuple_to_dict_list
from whoahqa.models import (
    ClinicFactory,
    Clinic,
)
import uuid
from pyenketo import Enketo


@view_defaults(route_name='clinics')
class ClinicViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=ClinicFactory,
                 renderer='clinics_list.jinja2')
    def list(self):
        # if the user doesnt have permissions to list all clinics,
        #  redirect to his own clinics
        if not has_permission(perms.LIST, self.request.context, self.request):
            return HTTPFound(
                self.request.route_url(
                    'users', traverse=(
                        self.request.ona_user.user_id, 'clinics')))

        # otherwise, list all clinics
        # TODO: paginate
        return {
            'can_list_clinics': True,
            'clinics': Clinic.all()
        }

    @view_config(name='unassigned',
                 context=ClinicFactory,
                 renderer='clinics_unassigned.jinja2')
    def unassigned(self):
        clinics = Clinic.get_unassigned()
        return {
            'clinics': clinics
        }

    @view_config(name='assign', request_method='POST', check_csrf=False)
    def assign(self):
        user = self.request.ona_user.user

        # get the list of requested clinics
        clinic_ids = self.request.POST.getall('clinic_id')
        clinics = Clinic.all(Clinic.id.in_(clinic_ids))
        for clinic in clinics:
            clinic.assign_to(user)
        return HTTPFound(
            self.request.route_url('clinics', traverse=('unassigned',)))

    @view_config(name='',
                 request_method='GET',
                 context=Clinic,
                 permission=perms.SHOW,
                 renderer='clinics_show.jinja2')
    def show(self):
        clinic = self.request.context

        # if clinic is not assigned, throw a bad request
        if not clinic.is_assigned:
            raise HTTPBadRequest("The clinic is not yet assigned")

        scores = clinic.get_scores()
        return {
            'clinic': clinic,
            'client_tools': tuple_to_dict_list(
                ("id", "name"), constants.CLIENT_TOOLS),
            'characteristics': tuple_to_dict_list(
                ("id", "description"), constants.CHARACTERISTICS),
            'scores': scores
        }

    @view_config(name='show_form',
                 request_method='GET')
    def show_form(self):
        # redirects to the survey form for specified survey
        survey_form = self.request.GET.get('form')
        # get enketo edit url
        enketo = Enketo()
        enketo.configure(
            self.request.registry.settings['enketo_url'],
            self.request.registry.settings['enketo_api_token'])
        try:
            survey_url = enketo.get_survey_url(
                self.request.registry.settings['form_server_url'],
                survey_form)

        except Http404:
            # Since enketo doesn't have the specified form throw a
            # bad request
            raise HTTPBadRequest("Survey Form not found")

        return HTTPFound(location=survey_url)

    @view_config(name='register',
                 context=ClinicFactory
                )
    def register_clinic(self):
        enketo = Enketo()
        enketo.configure(
            self.request.registry.settings['enketo_url'],
            self.request.registry.settings['enketo_api_token'])
        xml_instance = '<?xml version=\'1.0\' ?><clinic_registration id=\"clinic_registration\"><formhub><uuid>73242968f5754dc49c38463af658f3d2</uuid></formhub><user_id>{}</user_id><clinic_name></clinic_name><meta><instanceID>uuid:ec5ce15e-5a0a-4246-93fe-acf60ef69bf2</instanceID></meta></clinic_registration>'.format(
            self.request.ona_user.user_id)
        server_url = self.request.registry.settings['form_server_url']
        instance_id = uuid.uuid4()
        return_url = self.request.route_url(
                'users', traverse=(self.request.ona_user.user_id, 'clinics'))
        edit_url = enketo.get_edit_url(
            server_url,
            constants.CLINIC_REGISTRATION,
            xml_instance,
            instance_id,
            return_url
        )

        return HTTPFound(location=edit_url)

    @view_config(name='filterclinics',
                 request_method='POST',
                 check_csrf=False,
                 renderer='_clinics_table.jinja2')
    def filter_clinics(self):
        #filter list clinics by search term
        search_term = self.request.POST['st']
        all_clinics = self.request.POST['all_clinics']
        if all_clinics == 'true':
            all_clinics = True
        else:
            all_clinics = False
        s_clinics = Clinic.filter_clinics(search_term, all_clinics)
        return{
            'clinics': s_clinics,
            'search_term': search_term
        }
