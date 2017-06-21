import datetime

from webob.multidict import MultiDict
from pyramid import testing
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPFound
)
from httmock import urlmatch, HTTMock
from mock import patch

from sqlalchemy.orm.exc import NoResultFound

from whoahqa.constants import characteristics as constants
from whoahqa.utils import tuple_to_dict_list
from whoahqa.models import (
    DBSession,
    user_clinics,
    OnaUser,
    Clinic,
    Municipality,
    ReportingPeriod,
)
from whoahqa.views import (
    ClinicViews,
)
from whoahqa.tests import (IntegrationTestBase, FunctionalTestBase,)

WEBFORM_URL = 'https://iyt3v.enketo.org/webform'


@urlmatch(netloc=r'(.*\.)?test.enketo\.org$')
def fetch_survey_form_url(url, request):
    return {
        'status_code': 200,
        'content': '{"url": "%s"}' % WEBFORM_URL
    }


@urlmatch(netloc=r'(.*\.)?test.enketo\.org$')
def fetch_non_existent_survey_form_url(url, request):
    return {
        'status_code': 404,
        'content': '{"code": 404, "message": "form not found"}'
    }


@urlmatch(netloc='test.enketo.org', path='/api_v1/instance')
def enketo_edit_url_mock(url, request):
    return {
        'status_code': 201,
        'content':
        '{"code": 201, "edit_url": "http://test.enketo.org/edit?id=1"}'
    }


class TestClinicViews(IntegrationTestBase):
    def setUp(self):
        super(TestClinicViews, self).setUp()
        self.request = testing.DummyRequest()
        self.clinic_views = ClinicViews(self.request)
        self.setup_test_data()
        self._create_municipality("Brazilia")

    def test_unassigned_clinics_view(self):
        response = self.clinic_views.unassigned()

        # we should only have Clinic B in the response
        self.assertEqual(len(response['clinics']), 3)
        self.assertEqual(response['clinics'][0].name, "Clinic B")

        # test when filter is done
        params = MultiDict({'search': 'Clinic B'})
        self.request.GET = params
        response = self.clinic_views.unassigned()
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic B")
        self.assertEqual(response['search_term'], "Clinic B")

    def test_assign_view(self):
        count = DBSession.query(user_clinics).count()
        self.assertEqual(count, 1)

        ona_user = OnaUser.get(OnaUser.username == 'manager_a')

        # get the clinics
        clinics = Clinic.all()
        self.request.method = 'POST'
        self.request.user = ona_user.user
        params = MultiDict([('clinic_id', clinic.id) for clinic in clinics])
        self.request.POST = params
        self.clinic_views.assign()

        # both clinics should now be assigned to user
        count = DBSession.query(user_clinics).count()
        self.assertEqual(count, 4)

    def test_show(self):
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        clinic = Clinic.get(Clinic.id == 1)
        period.__parent__ = clinic
        self.request.context = period
        response = self.clinic_views.show()
        self.assertIsInstance(response['clinic'], Clinic)
        self.assertEqual(response['clinic'].id, clinic.id)
        self.assertIn('client_tools', response)
        self.assertEqual(
            response['characteristics'],
            tuple_to_dict_list(
                ("id", "description", "number"), constants.CHARACTERISTICS))

    def test_list_redirects_when_user_has_no_permissions(self):
        self.request.user = OnaUser.get(OnaUser.username == 'manager_a').user
        self.config.testing_securitypolicy(
            userid=2, permissive=False)
        response = self.clinic_views.list()
        self.assertEqual(response.status_code, 302)

        # test when filter is done
        params = MultiDict({'search': 'Clinic B'})
        self.request.GET = params
        response = self.clinic_views.unassigned()
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic B")
        self.assertEqual(response['search_term'], "Clinic B")

    def test_show_form(self):
        params = MultiDict({'form': constants.ADOLESCENT_CLIENT})
        self.request.GET = params
        with HTTMock(fetch_survey_form_url):
            response = self.clinic_views.show_form()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, WEBFORM_URL)

    def test_show_form_raises_bad_request_for_bad_form(self):
        params = MultiDict({'form': constants.ADOLESCENT_CLIENT})
        self.request.GET = params
        with HTTMock(fetch_non_existent_survey_form_url):
            self.assertRaises(HTTPBadRequest, self.clinic_views.show_form)

    def test_list_override_renderer_when_search_term_exists(self):
        self.request.GET = MultiDict([
            ('search', 'clinic a')
        ])
        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 6, 1)
            self.clinic_views.list()
            self.assertEqual(
                self.request.override_renderer, '_summary_scores_table.jinja2')

    def test_characteristics_list(self):
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        clinic = Clinic.get(Clinic.id == 1)
        period.__parent__ = clinic

        self.request.context = period
        response = self.clinic_views.characteristics_list()

        self.assertIsInstance(response['period'], ReportingPeriod)
        self.assertIsInstance(response['clinic'], Clinic)
        self.assertEqual(response['clinic'].id, clinic.id)
        self.assertEqual(response['characteristics'],
                         tuple_to_dict_list(
                             ("id", "description", "number"),
                             constants.CHARACTERISTICS)),
        self.assertEqual(response['indicator_labels'],
                         dict(constants.INDICATOR_LABELS)),
        self.assertEqual(response['characteristic_indicator_mapping'],
                         constants.CHARACTERISTIC_INDICATOR_MAPPING)

    def test_select_characteristics(self):
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        clinic = Clinic.get(Clinic.id == 1)
        period.__parent__ = clinic

        self.request.context = period
        params = MultiDict([
            ('characteristic_id', 'one'),
            ('characteristic_id', 'two'),
            ('characteristic_id', 'three')])

        self.request.POST = params
        response = self.clinic_views.select_characteristics()
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(response.location, self.request.route_url(
            'clinics', traverse=(clinic.id, period.id)))

    def test_characteristics_list_with_characteristic_type_filter(self):
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        clinic = Clinic.get(Clinic.id == 1)
        period.__parent__ = clinic
        self.request.context = period
        params = MultiDict({'char_type': 'equitable'})
        self.request.GET = params

        response = self.clinic_views.characteristics_list()

        self.assertIsInstance(response['period'], ReportingPeriod)
        self.assertIsInstance(response['clinic'], Clinic)
        self.assertEqual(response['clinic'].id, clinic.id)
        self.assertEqual(len(response['characteristics']), 3),
        self.assertEqual(response['indicator_labels'],
                         dict(constants.INDICATOR_LABELS)),
        self.assertEqual(response['characteristic_indicator_mapping'],
                         constants.CHARACTERISTIC_INDICATOR_MAPPING)

    def test_access_clinics_view(self):
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')

        self.request.method = 'GET'
        self.request.user = ona_user.user

        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 6, 1)
            response = self.clinic_views.assess_clinics()

            self.assertEqual(len(response['clinics']), 4)

    def test_manage_clinics_view(self):
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        self.request.method = 'GET'
        self.request.user = ona_user.user

        user_clinics = ona_user.user.location.clinics

        response = self.clinic_views.manage_clinics()

        self.assertEqual(response['clinics'], user_clinics)

    def test_delete_clinics(self):
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        user_clinics = ona_user.user.get_clinics()
        clinic = user_clinics[0]
        self.request.method = 'GET'
        self.request.user = ona_user.user
        self.request.context = clinic

        response = self.clinic_views.delete()

        self.assertEqual(response.status_code, 302)
        self.assertRaises(NoResultFound, Clinic.get, Clinic.id == clinic.id)

    def test_register_clinic_doesnt_save_clinics_with_same_codes(self):
        ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        municipality = Municipality.get(Municipality.name == "Brazilia")
        clinic = Clinic.get(Clinic.code == '1A2B')
        params = MultiDict({'municipality': "{}".format(municipality.id),
                            'name': "New Clinic Name",
                            'code': clinic.code})
        self.request.method = 'POST'
        self.request.ona_user = ona_user
        self.request.POST = params

        self.clinic_views.register_clinic()

        flash_error = self.request.session.pop_flash('error')[0]
        self.assertTrue(flash_error.find("exists") != -1)


class TestClinicViewsFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestClinicViewsFunctional, self).setUp()
        self.setup_test_data()
        self._create_municipality("Brazilia")
        self._create_user('john')

    def test_unassigned_clinics_view_allows_authenticated(self):
        url = self.request.route_path('clinics', traverse=('unassigned',))
        headers = self._login_user('manager_b')
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_assign_clinic_view_allows_authenticated(self):
        clinics = Clinic.all()
        url = self.request.route_path('clinics', traverse=('assign',))
        params = MultiDict([('clinic_id', clinic.id) for clinic in clinics])
        headers = self._login_user('manager_a')
        response = self.testapp.post(url, params, headers=headers)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            self.request.route_url('clinics', traverse=('unassigned',)))

    def test_clinic_show_allows_owner(self):
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        clinic = Clinic.get(Clinic.name == "Clinic A")
        url = self.request.route_path(
            'clinics', traverse=(clinic.id, period.id))
        headers = self._login_user('manager_a')
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_clinic_list_allows_super_user(self):
        url = self.request.route_path('clinics', traverse=())
        headers = self._login_user('super')
        with patch('whoahqa.models.reporting_period.get_current_date') as mock:
            mock.return_value = datetime.date(2015, 6, 1)
            response = self.testapp.get(url, headers=headers)
            self.assertEqual(response.status_code, 200)

    def test_characteristics_returns_200(self):
        clinic = Clinic.get(Clinic.name == "Clinic A")
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        url = self.request.route_path(
            'clinics', traverse=(clinic.id, period.id, 'characteristics'))
        headers = self._login_user('super')
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_manage_clinics(self):
        url = self.request.route_path(
            'clinics', traverse=('manage'))
        headers = self._login_user('manager_a')
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_view_manage_clinics(self):
        url = self.request.route_path(
            'clinics', traverse=('manage'))
        headers = self._login_user('john')
        response = self.testapp.get(url, headers=headers, status=403)
        self.assertEqual(response.status_code, 403)

    def test_register_clinic(self):
        headers = self._login_user('manager_a')
        url = self.request.route_path('clinics',
                                      traverse=('register'))
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_municipality_manager_can_edit_clinics(self):
        municipality = Municipality.get(Municipality.name == "Brazilia")
        clinic = Clinic.get(Clinic.code == '1A2B')
        url = self.request.route_path('clinics',
                                      traverse=(clinic.id, 'edit_clinic'))

        headers = self._login_user('manager_a')
        params = MultiDict({'municipality': municipality.id,
                            'name': "New Clinic Name",
                            'code': clinic.code})
        response = self.testapp.post(url, params, headers=headers)
        self.assertEqual(response.status_code, 200)
        clinic = Clinic.get(Clinic.code == '1A2B')

        self.assertEqual(clinic.name, "New Clinic Name")

    def test_access_clinic(self):
        self._create_user('jonah', 'municipality_manager')

        url = self.request.route_path(
            'clinics', traverse=('assess'))
        headers = self._login_user('jonah')
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
