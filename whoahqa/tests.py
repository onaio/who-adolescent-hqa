import unittest
import json
import transaction

from webob.multidict import MultiDict
from pyramid import testing
from pyramid.paster import (
    get_appsettings
)
from pyramid.httpexceptions import (
    HTTPBadRequest,
)
from pyramid.security import IAuthenticationPolicy
from sqlalchemy import engine_from_config
from webtest import TestApp

from whoahqa import main
from whoahqa.utils import tuple_to_dict_list
from whoahqa.models import (
    DBSession,
    Base,
    ClinicFactory,
    user_clinics,
    User,
    Clinic,
    Submission,
    ClinicSubmission,
    ClinicNotFound,
    CHARACTERISTICS,
    CHARACTERISTIC_MAPPING,
    ADOLESCENT_CLIENT,
    HEALTH_CARE_PROVIDER
)
from whoahqa.views import (
    ClinicViews,
    UserViews,
    SubmissionViews,
)


settings = get_appsettings('test.ini')
engine = engine_from_config(settings, 'sqlalchemy.')


class TestUtils(unittest.TestCase):
    def test_tuple_to_dict_list_creates_dict_from_list_of_tuples(self):
        result = tuple_to_dict_list(
            ("name", "age"),
            [("Billy", 12), ("Bob", 15)])
        self.assertEqual(result, [
            {"name": "Billy", "age": 12},
            {"name": "Bob", "age": 15}
        ])


class TestBase(unittest.TestCase):
    submissions = [
        '{"facility_info/clinic_id": "1A2B", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "health_facility_manager_interview_EnSp", "_geolocation": ["-1.2988785", "36.7905801"], "facility_info/facility_geopoint": "-1.2988785 36.7905801 0.0 36.452", "meta/instanceID": "uuid:478a3355-9fe9-44ab-a9c9-6a10cd50c827", "_status": "submitted_via_web", "characteristic_twenty/ch20_q3_yes": "Meds", "facility_info/HS_char": "twenty", "characteristic_twenty/ch20_q3": "0", "characteristic_twenty/ch20_q1": "1", "characteristic_twenty/ch20_q2": "1", "_uuid": "478a3355-9fe9-44ab-a9c9-6a10cd50c827", "facility_info/interviewer": "Larry", "respondent_dem/years_worked": "2", "formhub/uuid": "ae6ca5877a2949e58191e8029c465ebe", "_submission_time": "2014-02-03T11:06:36", "_attachments": [], "facility_info/interview_date": "2014-02-03", "_id": 23803}',
        '{"facility_info/clinic_id": "3E4G", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "male", "_xform_id_string": "adolescent_quality_assessmentEnSp", "respondent_dem/study_yes_Esp": "Yes", "_geolocation": ["-1.2988671", "36.7906039"], "respondent_dem/res_age": "18", "facility_info/facility_geopoint": "-1.2988671 36.7906039 0.0 34.208", "meta/instanceID": "uuid:a795726b-9989-4c70-ad92-93eb2c460b57", "_status": "submitted_via_web", "facility_info/HS_char": "twenty", "respondent_dem/study": "yes", "respondent_dem/marital_status": "single", "characteristic_twenty/ch20_q1": "1", "_uuid": "a795726b-9989-4c70-ad92-93eb2c460b57", "facility_info/interviewer": "Larry Weya", "respondent_dem/highest_study": "High school", "formhub/uuid": "dccae423c9704aa283b4a10343c916c9", "_submission_time": "2014-02-04T06:22:32", "_attachments": [], "facility_info/interview_date": "2014-02-03", "_id": 23936}',
        '{"facility_info/clinic_id": "1A2B", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "adolescent_quality_assementEnSp", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "1", "characteristic_three/ch3_q3": "0", "_uuid": "af18e938-8cb7-4a99-aa6d-35b05ae942d2", "characteristic_three/ch3_q4": "0", "facility_info/interviewer": "Kwhba", "respondent_dem/highest_study": "High school", "formhub/uuid": "753bba82422444eda5c4d05d39f73667", "characteristic_one/ch1_q2": "1", "characteristic_one/ch1_q1": "0", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/interview_date": "2014-02-06", "_id": 24651}',
        '{"facility_info/clinic_id": "1A2B", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "adolescent_quality_assementEnSp", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "0", "characteristic_three/ch3_q3": "0", "_uuid": "bd18e938-8cb7-4a99-aa6d-35b05ae942f1", "characteristic_three/ch3_q4": "1", "facility_info/interviewer": "Hwwk", "respondent_dem/highest_study": "Primary school", "formhub/uuid": "933bba82422444eda5c4d05d39f73684", "characteristic_one/ch1_q2": "1", "characteristic_one/ch1_q1": "1", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/interview_date": "2014-02-06", "_id": 24651}',
        '{"facility_info/clinic_id": "3E4G", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "adolescent_quality_assementEnSp", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "0", "characteristic_three/ch3_q3": "0", "_uuid": "ac18e938-8cb7-4a99-aa6d-35b05ae942d3", "characteristic_three/ch3_q4": "1", "facility_info/interviewer": "Hask", "respondent_dem/highest_study": "College", "formhub/uuid": "873bba82422444eda5c4d05d39f73616", "characteristic_one/ch1_q2": "0", "characteristic_one/ch1_q1": "1", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/interview_date": "2014-02-06", "_id": 24651}',
        '{"facility_info/clinic_id": "1A2B", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "male", "_xform_id_string": "health_care_provider_interview_EnSp", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "0", "characteristic_three/ch3_q3": "0", "_uuid": "ac18e938-8cb7-4a99-aa6d-35b05ae942d3", "characteristic_three/ch3_q4": "1", "facility_info/interviewer": "Hask", "respondent_dem/highest_study": "College", "formhub/uuid": "873bba82422444eda5c4d05d39f73616", "characteristic_one/ch1_q1": "1", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/interview_date": "2014-02-06", "_id": 24651}'
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
        clinic1 = Clinic(id=1, name="Clinic A", code="1A2B")
        # assign a user to clinic1
        user.clinics.append(clinic1)

        # leave clinic 2 unassigned
        clinic2 = Clinic(id=2, name="Clinic B", code="3E4G")

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

    # TODO: this test belongs elsewehere
    def test_each_characteristic_has_a_characteristic_mapping(self):
        keys = [c[0] for c in CHARACTERISTICS]
        mapping_keys = CHARACTERISTIC_MAPPING.keys()
        self.assertTrue(all([k in mapping_keys for k in keys]))


class TestUser(TestBase):
    def test_get_clinics(self):
        self.setup_test_data()
        user = User.newest()

        clinics = user.get_clinics()
        self.assertEqual(len(clinics), 1)
        self.assertEqual(clinics[0].name, "Clinic A")


class TestClinic(TestBase):
    def create_submissions(self):
        # make submissions
        for i in range(6):
            Submission.create_from_json(self.submissions[i])
        transaction.commit()

    def test_assign_to_user(self):
        self.setup_test_data()
        user = User.newest()
        clinic = DBSession.query(Clinic).filter_by(name="Clinic B").one()
        clinic.assign_to(user)
        user = DBSession.merge(user)
        clinic = DBSession.merge(clinic)
        self.assertEqual(clinic.user, user)

    def test_get_unassigned_clinics(self):
        self.setup_test_data()

        clinics = Clinic.get_unassigned()
        self.assertEqual(len(clinics), 1)
        self.assertEqual(clinics[0].name, "Clinic B")

    def test_calculate_score_works(self):
        self.setup_test_data()
        self.create_submissions()

        clinic = Clinic.get(Clinic.id == 1)
        score = clinic.calculate_score(
            'one', 'adolescent_quality_assementEnSp')
        self.assertEqual(score, (1.5, 2))

    def test_get_scores_works(self):
        """
        Test scores calculation for all characteristic and tool pairs per
        clinic
        """
        self.setup_test_data()
        self.create_submissions()

        clinic = Clinic.get(Clinic.id == 1)
        scores = clinic.get_scores()

        scores_1 = scores['one']
        self.assertEqual(scores_1[ADOLESCENT_CLIENT], {
            'aggregate_score': 1.5,
            'num_questions': 2,
            'num_responses': 2,
        })
        self.assertEqual(scores_1[HEALTH_CARE_PROVIDER], {
            'aggregate_score': 1,
            'num_questions': 1,
            'num_responses': 1,
        })

        self.assertEqual(scores_1['totals'], {
            'total_scores': 2.5,
            'total_questions': 5,
            'total_responses': 3,
            'total_percentage': 50.0
        })

    def test_get_scores_when_no_responses_sets_totals_to_none(self):
        self.setup_test_data()
        self.create_submissions()

        clinic = Clinic.get(Clinic.id == 1)
        scores = clinic.get_scores()

        scores_10 = scores['ten']
        self.assertEqual(scores_10[ADOLESCENT_CLIENT], {
            'aggregate_score': None,
            'num_questions': 4,
            'num_responses': 0,
        })

        self.assertEqual(scores_10['totals'], {
            'total_scores': None,
            'total_questions': 10,
            'total_responses': 0,
            'total_percentage': None
        })

    def test_calculate_score_when_no_responses_returns_none(self):
        self.setup_test_data()
        self.create_submissions()

        clinic = Clinic.get(Clinic.id == 1)
        score = clinic.calculate_score(
            'two', 'health_care_provider_interview_EnSp')
        self.assertEqual(score, (None, 0))

    def test_is_assigned_returns_true_if_assigned(self):
        self.setup_test_data()
        clinic_a = Clinic.get(Clinic.id == 1)
        self.assertTrue(clinic_a.is_assigned)

    def test_is_assigned_returns_false_if_not_assigned(self):
        self.setup_test_data()
        clinic_b = Clinic.get(Clinic.id == 2)
        self.assertFalse(clinic_b.is_assigned)


class TestSubmission(TestBase):
    def test_save_submission_with_valid_clinic_id(self):
        # create clinic with matching id
        clinic_code = "1A2B"
        clinic = Clinic(code=clinic_code, name="Clinic A")
        DBSession.add(clinic)

        # check current counts
        count = Submission.count()
        clinic_submission_count = ClinicSubmission.count()
        test_data = self.submissions[0]
        Submission.create_from_json(test_data)
        submission = Submission.newest()
        self.assertEqual(Submission.count(), count + 1)
        self.assertEqual(submission.raw_data, json.loads(test_data))

        # check that a clinic_submission record was created
        self.assertEqual(ClinicSubmission.count(), clinic_submission_count + 1)

    def test_save_submission_with_multiple_characteristics(self):
        # create clinic with matching id
        clinic_code = "1A2B"
        clinic = Clinic(code=clinic_code, name="Clinic A")
        DBSession.add(clinic)

        # check current counts
        count = Submission.count()
        clinic_submission_count = ClinicSubmission.count()
        test_data = self.submissions[2]
        Submission.create_from_json(test_data)
        submission = Submission.newest()
        self.assertEqual(Submission.count(), count + 1)
        self.assertEqual(submission.raw_data, json.loads(test_data))

        # check that 2 clinic_submission record was created
        self.assertEqual(ClinicSubmission.count(), clinic_submission_count + 2)

    def test_save_submission_with_invalid_clinic_id(self):
        count = Submission.count()
        clinic_submissions_count = ClinicSubmission.count()
        test_data = self.submissions[1]

        self.assertRaises(ClinicNotFound, Submission.create_from_json,
                          test_data)

        submission = Submission.newest()
        self.assertEqual(Submission.count(), count + 1)
        self.assertEqual(submission.raw_data, json.loads(test_data))
        self.assertEqual(clinic_submissions_count,
                         ClinicSubmission.count())

    def test_parse_json(self):
        parsed_json = Submission.parse_json(self.submissions[0])
        # we expect a structure with the determined clinic id (characteristics,
        # mapping of client tools to form ids)
        self.assertEqual(
            parsed_json,
            ("1A2B", ["twenty"], "health_facility_manager_interview_EnSp",))


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

        # we should only have Clinic B in the response
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic B")

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
        self.assertEqual(
            response['characteristics'],
            tuple_to_dict_list(("id", "description"), CHARACTERISTICS))

    def test_show_raises_bad_request_if_clinic_is_not_assigned(self):
        self.setup_test_data()
        clinic = Clinic.get(Clinic.id == 2)
        self.request.context = clinic
        self.assertRaises(HTTPBadRequest, self.clinic_views.show)


class TestUserViews(IntegrationTestBase):
    def test_user_clinics_view(self):
        self.setup_test_data()
        user = User.newest()
        request = testing.DummyRequest()
        request.context = user
        user_views = UserViews(request)
        response = user_views.clinics()

        # we should only have Clinic A in the response
        self.assertEqual(len(response['clinics']), 1)
        self.assertEqual(response['clinics'][0].name, "Clinic A")


class TestSubmissionViews(IntegrationTestBase):
    def post_json(self, payload=None):
        request = testing.DummyRequest()
        if payload:
            request.body = payload
        submission_view = SubmissionViews(request)
        return submission_view.json_post()

    def test_json_post_with_valid_clinic_id(self):
        clinic = Clinic(code='1A2B', name="Clinic A")
        DBSession.add(clinic)
        response = self.post_json(self.submissions[0])

        #should return a 201 response code
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.body, 'Saved')

    def test_null_json(self):
        response = self.post_json(None)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.comment, 'Missing JSON Payload')

    def test_json_post_with_invalid_clinic_id(self):
        clinic = Clinic(code='1A2B', name="Clinic A")
        DBSession.add(clinic)
        response = self.post_json(self.submissions[1])

        #should return a 201 response code
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.body,
                         'Accepted Pending Clinic Match')

    def test_json_post_without_clinic_id(self):
        response = self.post_json('{"test":"1234"}')

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
        clinic = Clinic.get(Clinic.id == 1)
        url = self.request.route_path('clinics', traverse=(clinic.id,))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_json_post(self):
        self.setup_test_data()
        url = self.request.route_path('submissions', traverse=())
        payload = self.submissions[2]
        response = self.testapp.post(url, payload)
        self.assertEqual(response.status_code, 201)