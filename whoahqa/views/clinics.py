import uuid

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
    Http404,
)

from whoahqa.utils import enketo
from whoahqa import constants
from whoahqa.constants import permissions as perms
from whoahqa.utils import tuple_to_dict_list, filter_dict_list_by_attr
from whoahqa.models import (
    ClinicFactory,
    Clinic,
    ReportingPeriod,
)


@view_defaults(route_name='clinics')
class ClinicViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=ClinicFactory,
                 renderer='clinics_list.jinja2',
                 request_method='GET')
    def list(self):
        # if the user doesnt have permissions to list all clinics,
        # redirect to his own clinics
        if not has_permission(perms.LIST, self.request.context, self.request):
            return HTTPFound(
                self.request.route_url(
                    'users', traverse=(
                        self.request.ona_user.user_id, 'clinics')))

        # otherwise, list all clinics
        # TODO: paginate
        # TODO: change renderer only if its an xhr request
        search_term = self.request.GET.get('search')
        if search_term is not None:
            clinics = Clinic.filter_clinics(search_term, True)
            self.request.override_renderer = '_clinics_table.jinja2'
        else:
            clinics = Clinic.all()

        return {
            'can_list_clinics': True,
            'clinics': clinics,
            'search_term': search_term
        }

    @view_config(name='unassigned',
                 context=ClinicFactory,
                 renderer='clinics_unassigned.jinja2',
                 request_method='GET'
                 )
    def unassigned(self):

        search_term = self.request.GET.get('search')
        if search_term is not None:
            clinics = Clinic.filter_clinics(search_term, False)
            self.request.override_renderer = '_clinics_table.jinja2'
        else:
            clinics = Clinic.get_unassigned()

        return {
            'clinics': clinics,
            'search_term': search_term
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
                 context=ReportingPeriod,
                 permission=perms.SHOW,
                 renderer='clinics_show.jinja2')
    def show(self):
        period = self.request.context
        clinic = period.__parent__
        # if clinic is not assigned, throw a bad request
        if not clinic.is_assigned:
            raise HTTPBadRequest("The clinic is not yet assigned")

        scores = clinic.get_scores()
        return {
            'period': period,
            'clinic': clinic,
            'client_tools': tuple_to_dict_list(
                ("id", "name"), constants.CLIENT_TOOLS),
            'characteristics': tuple_to_dict_list(
                ("id", "description", "number"), constants.CHARACTERISTICS),
            'recommended_sample_frame': constants.RECOMMENDED_SAMPLE_FRAMES,
            'scores': scores

        }

    @view_config(name='show_form',
                 request_method='GET')
    def show_form(self):
        # redirects to the survey form for specified survey
        survey_form = self.request.GET.get('form')
        # get enketo edit url
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
                 context=ClinicFactory)
    def register_clinic(self):
        xml_instance = '<?xml version=\'1.0\' ?><clinic_registration id=\"clinic_registration\"><formhub><uuid>73242968f5754dc49c38463af658f3d2</uuid></formhub><user_id>{}</user_id><clinic_name></clinic_name><meta><instanceID>uuid:ec5ce15e-5a0a-4246-93fe-acf60ef69bf2</instanceID></meta></clinic_registration>'.format(   # noqa
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

    @view_config(name='characteristics',
                 request_method='GET',
                 permission=perms.SHOW,
                 context=ReportingPeriod,
                 renderer='clinics_characteristics_list.jinja2')
    def characteristics_list(self):
        # get the reporting period from the GET params
        period = self.request.context
        clinic = period.__parent__
        user = clinic.user

        # if clinic is not assigned, throw a bad request
        if not clinic.is_assigned:
            raise HTTPBadRequest("The clinic is not yet assigned")

        scores = clinic.get_scores()
        characteristics = tuple_to_dict_list(
            ("id", "description", "number"), constants.CHARACTERISTICS)
        clinic_characteristics = clinic.get_active_characteristics(period)

        # filter out active characteristics
        active_characteristic_ids = [c.characteristic_id for c
                                     in clinic_characteristics]
        # filter out
        char_type = self.request.GET.get('char_type')
        filtered_characteristic_ids = []
        if char_type is not None and char_type != 'All':
            for key_char in tuple_to_dict_list(
                    ("id", "characteristics"), constants.KEY_INDICATORS):
                if key_char['id'] != char_type:
                    for char in key_char['characteristics']:
                        filtered_characteristic_ids.append(char)

        # merge active characteristics and characteristics to be removed
        # after filter
        merged_filter_list = \
            active_characteristic_ids + filtered_characteristic_ids

        inactive_characteristics = filter_dict_list_by_attr(
            merged_filter_list, characteristics, 'id', invert=True)

        return {
            'period': period,
            'clinic': clinic,
            'user': user,
            'client_tools': tuple_to_dict_list(
                ("id", "name"), constants.CLIENT_TOOLS),
            'characteristics': inactive_characteristics,
            'scores': scores,
            'indicator_labels': dict(constants.INDICATOR_LABELS),
            'characteristic_indicator_mapping':
            constants.CHARACTERISTIC_INDICATOR_MAPPING
        }

    @view_config(
        name='select_characteristics',
        context=ReportingPeriod,
        request_method='POST',
        check_csrf=False)
    def select_characteristics(self):

        period = self.request.context
        clinic = period.__parent__
        # get_clinic_id
        # get the list of selected characteristics
        characteristic_ids = self.request.POST.getall('characteristic_id')
        for characteristic_id in characteristic_ids:
            clinic.activate_characteristic(characteristic_id, period.id)

        return HTTPFound(
            self.request.route_url('clinics', traverse=(clinic.id, period.id)))
