import unittest
import transaction

from pyramid.registry import Registry
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
    User,
    Group,
    OnaUser,
    Clinic,
)


settings = get_appsettings('test.ini')
engine = engine_from_config(settings, 'sqlalchemy.')


class TestBase(unittest.TestCase):
    submissions = [
        '{"facility_info/clinic_id": "1A2B", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "health_facility_manager_interview_EnSp", "_geolocation": ["-1.2988785", "36.7905801"], "facility_info/facility_geopoint": "-1.2988785 36.7905801 0.0 36.452", "meta/instanceID": "uuid:478a3355-9fe9-44ab-a9c9-6a10cd50c827", "_status": "submitted_via_web", "characteristic_twenty/ch20_q3_yes": "Meds", "facility_info/HS_char": "twenty", "characteristic_twenty/ch20_q3": "0", "characteristic_twenty/ch20_q1": "1", "characteristic_twenty/ch20_q2": "1", "_uuid": "478a3355-9fe9-44ab-a9c9-6a10cd50c827", "facility_info/interviewer": "Larry", "respondent_dem/years_worked": "2", "formhub/uuid": "ae6ca5877a2949e58191e8029c465ebe", "_submission_time": "2014-02-03T11:06:36", "_attachments": [], "facility_info/interview_date": "2014-02-03", "_id": 23803}',
        '{"facility_info/clinic_id": "3E4G", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "male", "_xform_id_string": "adolescent_quality_assessmentEnSp", "respondent_dem/study_yes_Esp": "Yes", "_geolocation": ["-1.2988671", "36.7906039"], "respondent_dem/res_age": "18", "facility_info/facility_geopoint": "-1.2988671 36.7906039 0.0 34.208", "meta/instanceID": "uuid:a795726b-9989-4c70-ad92-93eb2c460b57", "_status": "submitted_via_web", "facility_info/HS_char": "twenty", "respondent_dem/study": "yes", "respondent_dem/marital_status": "single", "characteristic_twenty/ch20_q1": "1", "_uuid": "a795726b-9989-4c70-ad92-93eb2c460b57", "facility_info/interviewer": "Larry Weya", "respondent_dem/highest_study": "High school", "formhub/uuid": "dccae423c9704aa283b4a10343c916c9", "_submission_time": "2014-02-04T06:22:32", "_attachments": [], "facility_info/interview_date": "2014-02-03", "_id": 23936}',
        '{"facility_info/clinic_id": "1A2B", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "adolescent_quality_assessmentEnSp", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "1", "characteristic_three/ch3_q3": "0", "_uuid": "af18e938-8cb7-4a99-aa6d-35b05ae942d2", "characteristic_three/ch3_q4": "0", "facility_info/interviewer": "Kwhba", "respondent_dem/highest_study": "High school", "formhub/uuid": "753bba82422444eda5c4d05d39f73667", "characteristic_one/ch1_q2": "1", "characteristic_one/ch1_q1": "0", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/interview_date": "2014-02-06", "_id": 24651}',
        '{"facility_info/clinic_id": "1A2B", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "adolescent_quality_assessmentEnSp", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "0", "characteristic_three/ch3_q3": "0", "_uuid": "bd18e938-8cb7-4a99-aa6d-35b05ae942f1", "characteristic_three/ch3_q4": "1", "facility_info/interviewer": "Hwwk", "respondent_dem/highest_study": "Primary school", "formhub/uuid": "933bba82422444eda5c4d05d39f73684", "characteristic_one/ch1_q2": "1", "characteristic_one/ch1_q1": "1", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/interview_date": "2014-02-06", "_id": 24651}',
        '{"facility_info/clinic_id": "3E4G", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "adolescent_quality_assessmentEnSp", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "0", "characteristic_three/ch3_q3": "0", "_uuid": "ac18e938-8cb7-4a99-aa6d-35b05ae942d3", "characteristic_three/ch3_q4": "1", "facility_info/interviewer": "Hask", "respondent_dem/highest_study": "College", "formhub/uuid": "873bba82422444eda5c4d05d39f73616", "characteristic_one/ch1_q2": "0", "characteristic_one/ch1_q1": "1", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/interview_date": "2014-02-06", "_id": 24651}',
        '{"facility_info/clinic_id": "1A2B", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "male", "_xform_id_string": "health_care_provider_interview_EnSp", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "0", "characteristic_three/ch3_q3": "0", "_uuid": "ac18e938-8cb7-4a99-aa6d-35b05ae942d3", "characteristic_three/ch3_q4": "1", "facility_info/interviewer": "Hask", "respondent_dem/highest_study": "College", "formhub/uuid": "873bba82422444eda5c4d05d39f73616", "characteristic_one/ch1_q1": "1", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/interview_date": "2014-02-06", "_id": 24651}',
        # non existent clinic id
        '{"facility_info/clinic_id": "no-such-clinic", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "male", "_xform_id_string": "health_care_provider_interview_EnSp", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "0", "characteristic_three/ch3_q3": "0", "_uuid": "ac18e938-8cb7-4a99-aa6d-35b05ae942d3", "characteristic_three/ch3_q4": "1", "facility_info/interviewer": "Hask", "respondent_dem/highest_study": "College", "formhub/uuid": "873bba82422444eda5c4d05d39f73616", "characteristic_one/ch1_q1": "1", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/interview_date": "2014-02-06", "_id": 24651}'
    ]
    clinic_registrations = [
        '{"_notes": [], "_id": 27761, "user_id": "2", "_submission_time": "2014-02-20T09:24:40", "_uuid": "a3814ab2-6fcc-472b-9a7c-450d92b4fb10", "_bamboo_dataset_id": "", "_tags": [], "_attachments": [], "_geolocation": [null, null], "_xform_id_string": "clinic_registration", "_status": "submitted_via_web", "meta/instanceID": "uuid:a3814ab2-6fcc-472b-9a7c-450d92b4fb10", "clinic_name": "New Kakamega Clinic", "formhub/uuid": "4796cf1b830840b0a326cc16eda45083"}',
        # bad user id
        '{"_notes": [], "_id": 27761, "user_id": "-1", "_submission_time": "2014-02-20T09:24:40", "_uuid": "a3814ab2-6fcc-472b-9a7c-450d92b4fb10", "_bamboo_dataset_id": "", "_tags": [], "_attachments": [], "_geolocation": [null, null], "_xform_id_string": "clinic_registration", "_status": "submitted_via_web", "meta/instanceID": "uuid:a3814ab2-6fcc-472b-9a7c-450d92b4fb10", "clinic_name": "New Kakamega Clinic", "formhub/uuid": "4796cf1b830840b0a326cc16eda45083"}'
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
        su_group = Group(name='su')
        clinic_managers_group = Group(name='managers')

        su = User()
        su_ona_user = OnaUser(
            user=su, username='super', refresh_token="a123f4")
        su.groups.append(su_group)

        manager_a = User()
        manager_a_ona_user = OnaUser(
            user=manager_a, username='manager_a', refresh_token="b345d6")
        manager_a.groups.append(clinic_managers_group)

        manager_b = User()
        manager_b_ona_user = OnaUser(
            user=manager_b, username='manager_b', refresh_token="c563e9")
        manager_b.groups.append(clinic_managers_group)

        # add a couple of clinics
        clinic1 = Clinic(id=1, name="Clinic A", code="1A2B")
        # assign a su to clinic1
        manager_a.clinics.append(clinic1)

        # leave clinic 2 unassigned
        clinic2 = Clinic(id=2, name="Clinic B", code="3E4G")

        with transaction.manager:
            DBSession.add_all(
                [su_ona_user, manager_a_ona_user, manager_b_ona_user,
                 clinic1, clinic2])


class IntegrationTestBase(TestBase):
    def setUp(self):
        super(IntegrationTestBase, self).setUp()
        self.config.include('whoahqa')


class FunctionalTestBase(IntegrationTestBase):
    def _login_user(self, ona_username):
        user = OnaUser.get(OnaUser.username == ona_username).user
        policy = self.testapp.app.registry.queryUtility(IAuthenticationPolicy)
        headers = policy.remember(self.request, user.id)
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
