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
                 request_method='GET',
                 context=Clinic,
                 permission=perms.SHOW)
    def show_form(self):
        # redirects to the survey form for specified survey
        survey_form = self.request.GET.get('form')

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
