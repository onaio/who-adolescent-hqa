from webob.multidict import MultiDict
from pyramid import testing
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPFound
)
from httmock import urlmatch, HTTMock

from whoahqa import constants
from whoahqa.utils import tuple_to_dict_list
from whoahqa.models import (
    DBSession,
    user_clinics,
    OnaUser,
    Clinic,
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

    def test_unassigned_clinics_view(self):
        self.setup_test_data()
        response = self.clinic_views.unassigned()

        # we should only have Clinic B in the response
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic B")

        # test when filter is done
        params = MultiDict({'search': 'Clinic B'})
        self.request.GET = params
        response = self.clinic_views.unassigned()
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic B")
        self.assertEqual(response['search_term'], "Clinic B")

    def test_assign_view(self):
        self.setup_test_data()
        count = DBSession.query(user_clinics).count()
        self.assertEqual(count, 1)

        ona_user = OnaUser.get(OnaUser.username == 'manager_a')

        # get the clinics
        clinics = Clinic.all()
        self.request.method = 'POST'
        self.request.ona_user = ona_user
        params = MultiDict([('clinic_id', clinic.id) for clinic in clinics])
        self.request.POST = params
        self.clinic_views.assign()

        # both clinics should now be assigned to user
        count = DBSession.query(user_clinics).count()
        self.assertEqual(count, 2)

    def test_show(self):
        self.setup_test_data()
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        clinic = Clinic.get(Clinic.id == 1)
        period.__parent__ = clinic
        self.request.context = period
        response = self.clinic_views.show()
        self.assertIsInstance(response['clinic'], Clinic)
        self.assertEqual(response['clinic'].id, clinic.id)
        self.assertEqual(
            response['characteristics'],
            tuple_to_dict_list(
                ("id", "description", "number"), constants.CHARACTERISTICS))

    def test_show_raises_bad_request_if_clinic_is_not_assigned(self):
        self.setup_test_data()
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        clinic = Clinic.get(Clinic.name == "Clinic B")
        period.__parent__ = clinic
        self.request.context = period
        self.assertRaises(HTTPBadRequest, self.clinic_views.show)

    def test_list_redirects_when_user_has_no_permissions(self):
        self.setup_test_data()
        self.request.ona_user = OnaUser.get(OnaUser.username == 'manager_a')
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
        self.setup_test_data()
        params = MultiDict({'form': constants.ADOLESCENT_CLIENT})
        self.request.GET = params
        with HTTMock(fetch_survey_form_url):
            response = self.clinic_views.show_form()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, WEBFORM_URL)

    def test_show_form_raises_bad_request_for_bad_form(self):
        self.setup_test_data()
        params = MultiDict({'form': constants.ADOLESCENT_CLIENT})
        self.request.GET = params
        with HTTMock(fetch_non_existent_survey_form_url):
            self.assertRaises(HTTPBadRequest, self.clinic_views.show_form)

    def test_register_clinic(self):
        self.setup_test_data()
        self.request.ona_user = OnaUser.get(OnaUser.username == 'manager_a')
        with HTTMock(enketo_edit_url_mock):
            response = self.clinic_views.register_clinic()
        self.assertIsInstance(response, HTTPFound)

    def test_list_override_renderer_when_search_term_exists(self):
        self.request.GET = MultiDict([
            ('search', 'clinic a')
        ])
        self.clinic_views.list()
        self.assertEqual(
            self.request.override_renderer, '_clinics_table.jinja2')

    def test_characteristics_list(self):
        self.setup_test_data()
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
        self.setup_test_data()
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
        self.setup_test_data()
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


class TestClinicViewsFunctional(FunctionalTestBase):
    def test_unassigned_clinics_view_allows_authenticated(self):
        self.setup_test_data()
        url = self.request.route_path('clinics', traverse=('unassigned',))
        headers = self._login_user('manager_b')
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_assign_clinic_view_allows_authenticated(self):
        self.setup_test_data()
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
        self.setup_test_data()
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        clinic = Clinic.get(Clinic.name == "Clinic A")
        url = self.request.route_path(
            'clinics', traverse=(clinic.id, period.id))
        headers = self._login_user('manager_a')
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_clinic_list_allows_super_user(self):
        self.setup_test_data()
        url = self.request.route_path('clinics', traverse=())
        headers = self._login_user('super')
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_characteristics_returns_200(self):
        self.setup_test_data()
        clinic = Clinic.get(Clinic.name == "Clinic A")
        period = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        url = self.request.route_path(
            'clinics', traverse=(clinic.id, period.id, 'characteristics'))
        headers = self._login_user('super')
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
