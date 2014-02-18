import unittest
import json
import urlparse
import transaction

from webob.multidict import MultiDict
from pyramid.registry import Registry
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

from httmock import urlmatch, HTTMock

from whoahqa import main
from whoahqa.utils import tuple_to_dict_list
from whoahqa.security import group_finder
from whoahqa.models import (
    DBSession,
    Base,
    ClinicFactory,
    user_clinics,
    User,
    Group,
    OnaUser,
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
    oauth_authorize,
    oauth_callback,
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
        registry = Registry()
        registry.settings = settings
        self.config = testing.setUp(registry=registry)
        # setup db
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine
        # TODO: run migrations instead of create_all to test migrations
        Base.metadata.drop_all()
        Base.metadata.create_all()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def setup_test_data(self):
        su = User()
        su_ona_user = OnaUser(
            user=su, username='super', refresh_token="a123f4")
        # always persist this last as the test use User.newest to refer to
        # this user
        manager = User()
        manager_ona_user = OnaUser(
            user=manager, username='manager', refresh_token="b345d6")

        su_group = Group(name='su')
        su.groups.append(su_group)

        clinic_manager_group = Group(name='managers')
        manager.groups.append(clinic_manager_group)

        # add a couple of clinics
        clinic1 = Clinic(id=1, name="Clinic A", code="1A2B")
        # assign a su to clinic1
        manager.clinics.append(clinic1)

        # leave clinic 2 unassigned
        clinic2 = Clinic(id=2, name="Clinic B", code="3E4G")

        with transaction.manager:
            DBSession.add_all(
                [su_ona_user, manager_ona_user, clinic1, clinic2])


class IntegrationTestBase(TestBase):
    def setUp(self):
        super(IntegrationTestBase, self).setUp()
        self.config.include('whoahqa')


class TestSecurity(TestBase):
    def test_group_finder_returns_users_groups(self):
        self.setup_test_data()
        user = OnaUser.get(OnaUser.username == 'super').user

        request = testing.DummyRequest()
        groups = group_finder(user.id, request)
        self.assertListEqual(sorted(groups), sorted(['g:su', 'u:1']))

    def test_group_finder_returns_none_if_user_doesnt_exist(self):
        request = testing.DummyRequest()
        groups = group_finder(1234, request)
        self.assertIsNone(groups)


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
        user = OnaUser.get(OnaUser.username == 'manager').user

        clinics = user.get_clinics()
        self.assertEqual(len(clinics), 1)
        self.assertEqual(clinics[0].name, "Clinic A")


class TestOnaUser(TestBase):
    def test_get_or_create_from_api_data_creates_user(self):
        user_data = [{
            'username': u"user_one",
            'first_name': u"",
            'last_name': u""
        }]
        refresh_token = 'a123f4'
        ona_user = OnaUser.get_or_create_from_api_data(
            user_data,
            refresh_token)
        self.assertIsInstance(ona_user, OnaUser)
        self.assertIsInstance(ona_user.user, User)

    def test_get_or_create_from_api_data_returns_user_if_exists(self):
        user_data = [{
            'username': u"user_one",
            'first_name': u"",
            'last_name': u""
        }]
        # create the instance
        refresh_token = 'a123f4'
        OnaUser.get_or_create_from_api_data(user_data, refresh_token)

        # try to get or create
        new_refresh_token = 'b234f5'
        ona_user = OnaUser.get_or_create_from_api_data(
            user_data,
            new_refresh_token)
        self.assertIsInstance(ona_user, OnaUser)
        self.assertIsInstance(ona_user.user, User)
        self.assertEqual(ona_user.refresh_token, new_refresh_token)

    def test_get_or_create_from_api_data_raises_value_error_if_bad_json(self):
        user_data = [
            {
                'username': u"user_one",
                'first_name': u"",
                'last_name': u""
            }, {
                'username': u"user_one",
                'first_name': u"",
                'last_name': u""
            }]
        refresh_token = 'a123f4'
        self.assertRaises(
            ValueError,
            OnaUser.get_or_create_from_api_data,
            user_data,
            refresh_token)


class TestClinic(TestBase):
    def create_submissions(self):
        # make submissions
        for i in range(6):
            Submission.create_from_json(self.submissions[i])
        transaction.commit()

    def test_assign_to_user(self):
        self.setup_test_data()
        user = OnaUser.get(OnaUser.username == 'manager').user
        clinic = Clinic.get(Clinic.name == "Clinic B")
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

        user = OnaUser.get(OnaUser.username == 'manager').user

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
        user = OnaUser.get(OnaUser.username == 'manager').user
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


class TestAuth(IntegrationTestBase):
    def test_oauth_authorize(self):
        request = testing.DummyRequest()
        response = oauth_authorize(request)

        # redirect url
        self.assertEqual(response.status_code, 302)

        # parse the url
        parse_result = urlparse.urlparse(response.headers['Location'])
        # url must equal oauth_authorization_endpoint
        base_url = "{scheme}://{netloc}{path}".format(
            scheme=parse_result.scheme,
            netloc=parse_result.netloc,
            path=parse_result.path)
        oauth_authorization_endpoint = "{base_url}{path}".format(
            base_url=settings['oauth_base_url'],
            path=settings['oauth_authorization_path'])
        self.assertEqual(base_url, oauth_authorization_endpoint)

        # query params must include 1. correct client_id 2. required scopes
        # and 3. correct redirect url
        query_params = dict(urlparse.parse_qsl(parse_result.query))
        self.assertEqual(
            query_params['client_id'],
            settings['oauth_client_id'])
        self.assertEqual(query_params['scope'].split(),
                         ['read', 'groups'])
        self.assertEqual(
            query_params['redirect_uri'],
            request.route_url('auth', action="callback"))

        # test that the `oauth_state` is saved in the session
        self.assertIn('oauth_state', request.session)

    def test_oauth_authorize_accepted(self):
        pass

    def test_oauth_authorize_canceled(self):
        request = testing.DummyRequest()
        request.GET = MultiDict([
            ('error', u"access_denied"), ('state', 'a123f4')])
        response = oauth_callback(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers['Location'],
            request.route_url('auth', action='login'))


class FunctionalTestBase(IntegrationTestBase):
    def _login_user(self, user_id):
        policy = self.testapp.app.registry.queryUtility(IAuthenticationPolicy)
        headers = policy.remember(self.request, user_id)
        cookie_parts = dict(headers)['Set-Cookie'].split('; ')
        cookie = filter(
            lambda i: i.split('=')[0] == 'auth_tkt', cookie_parts)[0]
        return {'Cookie': cookie}

    def setUp(self):
        super(FunctionalTestBase, self).setUp()
        app = main({}, **settings)
        self.testapp = TestApp(app, extra_environ={
            'HTTP_HOST': 'example.com'
        })
        self.request = testing.DummyRequest()
        # used by cookie auth as the domain
        self.request.environ = {
            'SERVER_NAME': 'example.com',
        }


class TestClinicViewsFunctional(FunctionalTestBase):
    def test_unassigned_clinics_view(self):
        url = self.request.route_path('clinics', traverse=('unassigned',))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_assign_clinic_view(self):
        self.setup_test_data()
        user = OnaUser.get(OnaUser.username == 'manager').user
        headers = self._login_user(user.id)

        clinics = Clinic.all()
        url = self.request.route_path('clinics', traverse=('assign',))
        params = MultiDict([('clinic_id', clinic.id) for clinic in clinics])
        response = self.testapp.post(url, params, headers=headers)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            self.request.route_url('clinics', traverse=('unassigned',)))

    def test_clinic_show(self):
        self.setup_test_data()
        clinic = Clinic.get(Clinic.id == 1)
        url = self.request.route_path('clinics', traverse=(clinic.id,))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)


class TestUserViewsFunctional(FunctionalTestBase):
    def test_user_clinics_view_allows_owner(self):
        self.setup_test_data()
        url = self.request.route_path('users', traverse=('1', 'clinics'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)


class TestSubmissionViewsFunctional(FunctionalTestBase):
    def test_json_post(self):
        self.setup_test_data()
        url = self.request.route_path('submissions', traverse=())
        payload = self.submissions[2]
        response = self.testapp.post(url, payload)
        self.assertEqual(response.status_code, 201)


class TestAuthFunctional(FunctionalTestBase):
    @staticmethod
    @urlmatch(netloc='accounts.example.com', path='/o/token')
    def oauth_token_mock(url, request):
        return {
            'status_code': 200,
            'content': '{"access_token":"1/fFAGRNJru1FTz70BzhT3Zg", "expires_in":3920, "token_type":"Bearer", "refresh_token":"1/f4YTbBjMoBbXfg7oFh_FKg6r3r6bh8M9Y-0"}'
        }

    @staticmethod
    @urlmatch(netloc='accounts.example.com', path='/api/v1/users')
    def oauth_users_mock(url, request):
        return {
            'status_code': 200,
            'content': '[{"username": "user_one", "first_name": "", "last_name": ""}]'
        }

    def test_login_response(self):
        url = self.request.route_url('auth', action='login')
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_oauth_authorize_accepted(self):
        state = 'a123f4'
        code = 'f27299'
        url = self.request.route_path('auth', action='callback')
        with HTTMock(TestAuthFunctional.oauth_token_mock,
                     TestAuthFunctional.oauth_users_mock):
            response = self.testapp.get(url, params={
                'state': state,
                'code': code
            })

        # test that user is gotten or created
        ona_user = OnaUser.get(OnaUser.username == 'user_one')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            self.request.route_url(
                'users', traverse=(ona_user.user.id, 'clinics')))

        # check that we set the login header
        self.assertIn('Set-Cookie', response.headers)
