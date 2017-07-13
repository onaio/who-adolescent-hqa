from deform import Form, ValidationFailure, Button

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

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from whoahqa.utils import (
    enketo,
    translation_string_factory as _)
from whoahqa.constants import characteristics as constants
from whoahqa.constants import permissions as perms
from whoahqa.views.helpers import get_period_from_request

from whoahqa.utils import tuple_to_dict_list, filter_dict_list_by_attr
from whoahqa.models import (
    ClinicFactory,
    Clinic,
    DBSession,
    Municipality,
    ReportingPeriod,
)
from whoahqa.forms import ClinicForm
from whoahqa.views.base import BaseClassViews


FORM_MAP = {
    'adolescent_client_V3': 215285,
    'health_care_provider_V3': 215288,
    'support_staff_V3': 215292,
    'health_facility_manager_V3': 215289,
    'outreach_worker_V3': 215291,
    'community_member_V3': 215287,
    'adolescent_in_community_V3': 215286,
    'observation_guide_V3': 215290,
}


@view_defaults(route_name='clinics')
class ClinicViews(BaseClassViews):
    @view_config(name='',
                 context=ClinicFactory,
                 renderer='clinics_summary.jinja2',
                 request_method='GET')
    def list(self):
        # if the user doesnt have permissions to list all clinics,
        # redirect to his own clinics
        if not self.request.has_permission(perms.CAN_VIEW_MUNICIPALITY,
                                           self.request.context):
            return HTTPFound(
                self.request.route_url(
                    'users', traverse=(
                        self.request.user.id, 'clinics')))

        # otherwise, list all clinics
        # TODO: paginate
        # TODO: change renderer only if its an xhr request
        search_term = self.request.GET.get('search')

        if search_term is not None:
            clinics = Clinic.filter_clinics(search_term, True)
            self.request.override_renderer = '_summary_scores_table.jinja2'
        else:
            clinics = self.request.user.clinics

        state = None
        municipality = None

        if clinics:
            municipality = clinics[0].municipality
            state = municipality.parent

        return {
            'locations': clinics,
            'municipality': municipality,
            'national_report': self.national_report(self.period),
            'period': self.period,
            'periods': self.periods,
            'key_indicators_key_labels': self.key_indicators_key_labels,
            'state': state
        }

    @view_config(name='',
                 request_method='GET',
                 context=ReportingPeriod,
                 permission=perms.CAN_VIEW_CLINICS,
                 renderer='clinics_show.jinja2')
    def show(self):
        period = self.request.context
        clinic = period.__parent__

        # if clinic is not assigned, throw a bad request
        # if not clinic.is_assigned:
        #     raise HTTPBadRequest("The clinic is not yet assigned")

        scores = clinic.get_scores(period.form_xpath)

        return {
            'period': period,
            'periods': ReportingPeriod.get_active_periods(),
            'clinic': clinic,
            'characteristics': tuple_to_dict_list(
                ("id", "description", "number"), constants.CHARACTERISTICS),
            'client_tools': tuple_to_dict_list(
                ("id", "name"), constants.CLIENT_TOOLS),
            'recommended_sample_frame': constants.RECOMMENDED_SAMPLE_FRAMES,
            'key_indicators': constants.KEY_INDICATORS,
            'scores': scores

        }

    @view_config(name='show_form',
                 request_method='GET')
    def show_form(self):
        # redirects to the survey form for specified survey
        survey_form = self.request.GET.get('form')
        survey_id = FORM_MAP.get(survey_form)
        # get enketo edit url
        try:
            survey_url = enketo.get_survey_url(
                "%s/%s" % (
                    self.request.registry.settings['form_server_url'],
                    survey_id),
                survey_form)
        except Http404:
            # Since enketo doesn't have the specified form throw a
            # bad request
            raise HTTPBadRequest("Survey Form not found")

        return HTTPFound(location=survey_url)

    @view_config(name='characteristics',
                 request_method='GET',
                 permission=perms.CAN_VIEW_CLINICS,
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

        scores = clinic.get_scores(period.form_xpath)
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
        require_csrf=False)
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

    @view_config(
        name='manage',
        renderer='clinics_list.jinja2',
        request_method='GET',
        permission=perms.CAN_LIST_CLINICS)
    def manage_clinics(self):
        user = self.request.user

        if self.request.has_permission(perms.SUPER_USER,
                                       self.request.context):
            clinics = Clinic.all()
        else:
            clinics = user.location.clinics

        period = get_period_from_request(self.request)
        return {
            'clinics': clinics,
            'period': period
        }

    @view_config(name='register',
                 context=ClinicFactory,
                 renderer='clinics_edit.jinja2',
                 permission=perms.CAN_EDIT_CLINICS)
    def register_clinic(self):
        clinic = Clinic()
        period = get_period_from_request(self.request)

        form = Form(
            ClinicForm().bind(
                request=self.request,
                clinic=clinic),
            button=('Save', Button(name='cancel', type='button')),
            appstruct=clinic.appstruct)

        if self.request.method == 'POST':
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                pass
            else:
                try:
                    municipality = Municipality.get(
                        Municipality.id == values.get('municipality'))
                    clinic.update(values.get('name'),
                                  values.get('code'),
                                  municipality)
                    self.request.session.flash(
                        _("{} saved.".format(clinic.name)), "success")

                    return HTTPFound(
                        self.request.route_url(
                            'clinics',
                            traverse=(clinic.id, 'edit_clinic')))

                except NoResultFound:
                    self.request.session.flash(
                        _("Cannot find selected municipality."), "error")

                except IntegrityError:
                    DBSession.rollback()

                    self.request.session.flash(
                        _("A clinic already exists with the \
                          provided CNES."),
                        "error")

        return {
            'form': form,
            'clinic': clinic,
            'period': period
        }

    @view_config(
        name='edit_clinic',
        renderer='clinics_edit.jinja2',
        context=Clinic,
        permission=perms.CAN_EDIT_CLINICS)
    def edit_clinics(self):
        clinic = self.request.context

        form = Form(
            ClinicForm().bind(
                request=self.request,
                clinic=clinic),
            button=('Save', Button(name='cancel', type='button')),
            appstruct=clinic.appstruct)

        if self.request.method == 'POST':
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                pass
            else:
                try:
                    municipality = Municipality.get(
                        Municipality.id == values.get('municipality'))
                    clinic.update(values.get('name'),
                                  values.get('code'),
                                  municipality)
                    self.request.session.flash(
                        _("{} updated.".format(clinic.name)), "success")

                except NoResultFound:
                    self.request.session.flash(
                        _("Cannot find selected municipality."), "error")

                except IntegrityError:
                    DBSession.rollback()

                    self.request.session.flash(
                        ("A clinic already exists with the \
                          provided CNES."),
                        "error")

        period = get_period_from_request(self.request)

        return {
            'form': form,
            'clinic': clinic,
            'period': period
        }

    @view_config(
        name='delete',
        renderer='clinics_edit.jinja2',
        context=Clinic,
        permission=perms.CAN_EDIT_CLINICS)
    def delete(self):
        clinic = self.request.context
        DBSession.delete(clinic)

        return HTTPFound(
            location=self.request.route_url('clinics', traverse=('manage')))

    @view_config(
        name='assess',
        renderer='clinics_assess.jinja2',
        request_method='GET',
        permission=perms.CAN_ASSESS_CLINICS)
    def assess_clinics(self):
        user = self.request.user
        clinics = []

        if user.location:
            clinics = user.location.clinics

        period = get_period_from_request(self.request)

        return {
            'clinics': clinics,
            'period': period,
            'periods': ReportingPeriod.get_active_periods(),
            'client_tools': tuple_to_dict_list(
                ("id", "name"), constants.CLIENT_TOOLS),
            'recommended_sample_frame': constants.RECOMMENDED_SAMPLE_FRAMES,
        }
