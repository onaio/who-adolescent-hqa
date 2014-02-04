import unittest
import transaction

from webob.multidict import MultiDict
from pyramid import testing
from pyramid.paster import (
    get_appsettings
)
from pyramid.security import IAuthenticationPolicy
from sqlalchemy import engine_from_config
from webtest import TestApp

from whoahqa import main
from whoahqa.models import (
    DBSession,
    Base,
    ClinicFactory,
    user_clinics,
    User,
    Clinic,
    Submission,
    ClinicSubmission,
    ClinicNotFound
)
from whoahqa.views import (
    ClinicViews,
    UserViews,
    SubmissionViews,
)


settings = get_appsettings('test.ini')
engine = engine_from_config(settings, 'sqlalchemy.')


class TestBase(unittest.TestCase):
    submissions = [
        '{"clinic_id": "abcd", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "health_facility_manager_interview", "_geolocation": ["-1.2988785", "36.7905801"], "facility_info/facility_geopoint": "-1.2988785 36.7905801 0.0 36.452", "meta/instanceID": "uuid:478a3355-9fe9-44ab-a9c9-6a10cd50c827", "_status": "submitted_via_web", "characteristic_twenty/ch20_q3_yes": "Meds", "facility_info/HS_char": "twenty", "characteristic_twenty/ch20_q3": "0", "characteristic_twenty/ch20_q1": "1", "characteristic_twenty/ch20_q2": "1", "_uuid": "478a3355-9fe9-44ab-a9c9-6a10cd50c827", "facility_info/interviewer": "Larry", "respondent_dem/years_worked": "2", "formhub/uuid": "ae6ca5877a2949e58191e8029c465ebe", "_submission_time": "2014-02-03T11:06:36", "_attachments": [], "facility_info/interview_date": "2014-02-03", "_id": 23803}',
        '{"clinic_id": "efgh", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "male", "_xform_id_string": "adolescent_quality_assessmentEnSp", "respondent_dem/study_yes_Esp": "Yes", "_geolocation": ["-1.2988671", "36.7906039"], "respondent_dem/res_age": "18", "facility_info/facility_geopoint": "-1.2988671 36.7906039 0.0 34.208", "meta/instanceID": "uuid:a795726b-9989-4c70-ad92-93eb2c460b57", "_status": "submitted_via_web", "facility_info/HS_char": "twenty", "respondent_dem/study": "yes", "respondent_dem/marital_status": "single", "characteristic_twenty/ch20_q1": "1", "_uuid": "a795726b-9989-4c70-ad92-93eb2c460b57", "facility_info/interviewer": "Larry Weya", "respondent_dem/highest_study": "High school", "formhub/uuid": "dccae423c9704aa283b4a10343c916c9", "_submission_time": "2014-02-04T06:22:32", "_attachments": [], "facility_info/interview_date": "2014-02-03", "_id": 23936}'
    ]

    def setUp(self):
        self.config = testing.setUp()
        # setup db
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine
        Base.metadata.drop_all()
        Base.metadata.create_all()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def setup_test_data(self):
        user = User()

        # add a couple of clinics
        clinic1 = Clinic(id=1, name="Clinic No. 1", identifier="wxyz")
        # assign a user to clinic1
        user.clinics.append(clinic1)

        # leave clinic 2 unassigned
        clinic2 = Clinic(id=2, name="Clinic No. 2", identifier="ijkl")

        with transaction.manager:
            DBSession.add_all([user, clinic1, clinic2])


class IntegrationTestBase(TestBase):
    def setUp(self):
        super(IntegrationTestBase, self).setUp()
        self.config.include('whoahqa')


class TestSetRequestUser(TestBase):
    def test_sets_user_if_id_exists(self):
        pass

    def test_sets_none_if_id_doesnt_exist(self):
        pass


class TestBaseModel(TestBase):
    def test_newest_returns_newest_record_by_id_desc(self):
        user1 = User(id=1)
        user2 = User(id=2)
        with transaction.manager:
            DBSession.add_all([user1, user2])
        user = User.newest()
        self.assertEqual(user.id, 2)

    def test_get_returns_record_filtered_by_criterion(self):
        user = User(id=1)
        with transaction.manager:
            DBSession.add(user)
        user = User.get(User.id == 1)
        self.assertIsInstance(user, User)

    def test_all_returns_multiple_matches_filtered_by_criterion(self):
        self.setup_test_data()
        clinics = Clinic.all(Clinic.id.in_([1, 2]))
        self.assertEqual(len(clinics), 2)

    def test_count_returns_count_filtered_by_criterion(self):
        self.setup_test_data()
        count = Clinic.count(Clinic.id.in_([1, 2]))
        self.assertEqual(count, 2)


class TestUser(TestBase):
    def test_get_clinics(self):
        self.setup_test_data()
        user = User.newest()

        clinics = user.get_clinics()
        self.assertEqual(len(clinics), 1)
        self.assertEqual(clinics[0].name, "Clinic No. 1")


class TestClinic(TestBase):
    def test_assign_to_user(self):
        self.setup_test_data()
        user = User.newest()
        clinic = DBSession.query(Clinic).filter_by(name="Clinic No. 2").one()
        clinic.assign_to(user)
        user = DBSession.merge(user)
        clinic = DBSession.merge(clinic)
        self.assertEqual(clinic.user, user)

    def test_get_unassigned_clinics(self):
        self.setup_test_data()

        clinics = Clinic.get_unassigned()
        self.assertEqual(len(clinics), 1)
        self.assertEqual(clinics[0].name, "Clinic No. 2")


class TestSubmission(TestBase):
    def test_save_submission_with_valid_clinic_id(self):
        # create clinic with matching id
        clinic_identifier = "abcd"
        clinic = Clinic(identifier=clinic_identifier, name="Clinic A")
        DBSession.add(clinic)

        # check current counts
        count = Submission.count()
        clinic_submission_count = ClinicSubmission.count()
        test_data = self.submissions[0]
        Submission.save(test_data)
        submission = Submission.newest()
        self.assertEqual(Submission.count(), count + 1)
        self.assertEqual(submission.raw_data, test_data)

        # check that a clinic_submission record was created
        self.assertEqual(ClinicSubmission.count(), clinic_submission_count + 1)

    def test_save_submission_with_invalid_clinic_id(self):
        count = Submission.count()
        clinic_submissions_count = ClinicSubmission.count()
        test_data = self.submissions[1]

        self.assertRaises(ClinicNotFound, Submission.save, test_data)

        submission = Submission.newest()
        self.assertEqual(Submission.count(), count + 1)
        self.assertEqual(submission.raw_data, test_data)
        self.assertEqual(clinic_submissions_count,
                         ClinicSubmission.count())

    def test_parse_json(self):
        parsed_json = Submission.parse_json(self.submissions[0])
        # we expect a structure with the determined clinic id (characteristic,
        # mapping of client tools to form ids)
        self.assertEqual(parsed_json, {
            'clinic_id': "abcd",
            'characteristic': "twenty",
            'xform_id': "health_facility_manager_interview"
        })


class TestUserFactory(TestBase):
    def test_get_item_returns_clinic_if_id_exists(self):
        self.setup_test_data()
        clinic = Clinic.newest()

        request = testing.DummyRequest()
        clinic = ClinicFactory(request).__getitem__(clinic.id)
        self.assertIsInstance(clinic, Clinic)

    def test_get_item_raises_key_error_if_id_doesnt_exist(self):
        # invalid clinic id
        clinic_id = -1

        request = testing.DummyRequest()
        self.assertRaises(KeyError,
                          ClinicFactory(request).__getitem__, clinic_id)


class TestClinicFactory(TestBase):
    def test_get_item_returns_clinic_if_id_exists(self):
        self.setup_test_data()
        clinic = Clinic.newest()

        request = testing.DummyRequest()
        clinic = ClinicFactory(request).__getitem__(clinic.id)
        self.assertIsInstance(clinic, Clinic)

    def test_get_item_raises_key_error_if_id_doesnt_exist(self):
        # invalid user id
        clinic_id = -1

        request = testing.DummyRequest()
        self.assertRaises(KeyError,
                          ClinicFactory(request).__getitem__, clinic_id)


class TestClinicViews(IntegrationTestBase):
    def setUp(self):
        super(TestClinicViews, self).setUp()
        self.request = testing.DummyRequest()
        self.clinic_views = ClinicViews(self.request)

    def test_unassigned_clinics_view(self):
        self.setup_test_data()
        response = self.clinic_views.unassigned()

        # we should only have Clinic No. 2 in the response
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic No. 2")

    def test_assign_view(self):
        self.setup_test_data()
        count = DBSession.query(user_clinics).count()
        self.assertEqual(count, 1)

        user = User.newest()

        # get the clinics
        clinics = Clinic.all()
        self.request.method = 'POST'
        self.request.user = user
        params = MultiDict([('clinic_id', clinic.id) for clinic in clinics])
        self.request.POST = params
        response = self.clinic_views.assign()

        # both clinics should now be assigned to user
        count = DBSession.query(user_clinics).count()
        self.assertEqual(count, 2)

    def test_show(self):
        self.setup_test_data()
        clinic = Clinic.get(Clinic.id == 1)
        self.request.context = clinic
        response = self.clinic_views.show()
        self.assertIsInstance(response['clinic'], Clinic)
        self.assertEqual(response['clinic'].id, clinic.id)


class TestUserViews(IntegrationTestBase):
    def test_user_clinics_view(self):
        self.setup_test_data()
        user = User.newest()
        request = testing.DummyRequest()
        request.context = user
        user_views = UserViews(request)
        response = user_views.clinics()

        # we should only have Clinic No. 1 in the response
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic No. 1")


class TestSubmissionViews(IntegrationTestBase):
    def make_submission(self, payload=None):
        request = testing.DummyRequest()
        if payload:
            request.POST['payload'] = payload
        submission_view = SubmissionViews(request)
        return submission_view.json_post()

    def test_json_post_with_valid_clinic_id(self):
        clinic = Clinic(identifier='abcd', name="Clinic A")
        DBSession.add(clinic)
        response = self.make_submission(self.submissions[0])

        #should return a 201 response code
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.body, 'Saved')

    def test_null_json(self):
        response = self.make_submission(None)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.comment, 'Missing JSON Payload')

    def test_json_post_with_invalid_clinic_id(self):
        clinic = Clinic(identifier='abcd', name="Clinic A")
        DBSession.add(clinic)
        response = self.make_submission(self.submissions[1])

        #should return a 201 response code
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.body,
                         'Accepted Pending Clinic Match')

    def test_json_post_without_clinic_id(self):
        response = self.make_submission('{"test":"1234"}')

        #should return a 202 response code
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.body,
                         'Accepted Pending Clinic Match')


class FunctionalTestBase(IntegrationTestBase):
    def setUp(self):
        super(FunctionalTestBase, self).setUp()
        app = main({}, **settings)
        self.testapp = TestApp(app)
        self.request = testing.DummyRequest()
        self.request.environ = {
            'SERVER_NAME': 'example.com',
        }


class TestViewsFunctional(FunctionalTestBase):
    def _login_user(self, user_id):
        policy = self.testapp.app.registry.queryUtility(IAuthenticationPolicy)
        headers = policy.remember(self.request, user_id)
        cookie_parts = dict(headers)['Set-Cookie'].split('; ')
        cookie = filter(
            lambda i: i.split('=')[0] == 'auth_tkt', cookie_parts)[0]
        return {'Cookie': cookie}

    def test_unassigned_clinics_view(self):
        url = self.request.route_path('clinics', traverse=('unassigned',))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_clinics_view(self):
        self.setup_test_data()
        url = self.request.route_path('users', traverse=('1', 'clinics'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_assign_clinic_view(self):
        self.setup_test_data()
        user = User.newest()
        headers = self._login_user(user.id)

        clinics = Clinic.all()
        url = self.request.route_path('clinics', traverse=('assign',))
        params = MultiDict([('clinic_id', clinic.id) for clinic in clinics])
        response = self.testapp.post(url, params, headers=headers)
        self.assertEqual(response.status_code, 302)
        path = self.request.route_path('clinics', traverse=('unassigned',))
        # TODO: have request use example.com as host
        self.assertEqual(response.location, "http://localhost{}".format(path))

    def test_clinic_show(self):
        self.setup_test_data()
        user = User.newest()

        clinic = Clinic.get(Clinic.id == 1)
        url = self.request.route_path('clinics', traverse=(clinic.id,))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)