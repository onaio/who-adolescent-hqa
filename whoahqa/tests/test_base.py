import os
import unittest
import transaction
import datetime

from pyramid.registry import Registry
from pyramid import testing
from pyramid.paster import (
    get_appsettings
)
from pyramid.security import IAuthenticationPolicy
from sqlalchemy import engine_from_config
from webtest import TestApp

from whoahqa import main
from whoahqa.constants import groups
from whoahqa.utils import enketo
from whoahqa.security import pwd_context
from whoahqa.models import (
    DBSession,
    Base,
    User,
    UserSettings,
    Group,
    Submission,
    OnaUser,
    Clinic,
    Municipality,
    ReportingPeriod
)


SETTINGS_FILE = 'test.ini'
settings = get_appsettings(SETTINGS_FILE)
engine = engine_from_config(settings, 'sqlalchemy.')


class TestBase(unittest.TestCase):
    submissions = [
        # clinic.id = 1 submissions
        '{"facility_info/facility_cnes": "1A2B", "facility_info/municipality": "Brasilia", "facility_info/state": "Acre", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "health_facility_manager_interview", "_geolocation": ["-1.2988785", "36.7905801"], "facility_info/facility_geopoint": "-1.2988785 36.7905801 0.0 36.452", "meta/instanceID": "uuid:478a3355-9fe9-44ab-a9c9-6a10cd50c827", "_status": "submitted_via_web", "characteristic_twenty/ch20_q3_yes": "Meds", "facility_info/HS_char": "twenty", "characteristic_twenty/ch20_q3": "0", "characteristic_twenty/ch20_q1": "1", "characteristic_twenty/ch20_q2": "1", "_uuid": "478a3355-9fe9-44ab-a9c9-6a10cd50c827", "facility_info/interviewer": "Larry", "respondent_dem/years_worked": "2", "formhub/uuid": "ae6ca5877a2949e58191e8029c465ebe", "_submission_time": "2014-02-03T11:06:36", "_attachments": [], "facility_info/interview_date": "2014-02-03", "_id": 23803}',  # noqa
        '{"facility_info/facility_cnes": "1A2B", "facility_info/municipality": "Brasilia", "facility_info/state": "Acre", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "adolescent_client_interview", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "1", "characteristic_three/ch3_q3": "0", "_uuid": "af18e938-8cb7-4a99-aa6d-35b05ae942d2", "characteristic_three/ch3_q4": "0", "facility_info/interviewer": "Kwhba", "respondent_dem/highest_study": "High school", "formhub/uuid": "753bba82422444eda5c4d05d39f73667", "characteristic_one/ch1_q2": "1", "characteristic_one/ch1_q1": "0", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/reporting_period": "2014-02-06", "facility_info/interview_date": "2014-02-06", "_id": 24651}',  # noqa
        '{"facility_info/facility_cnes": "1A2B", "facility_info/municipality": "Brasilia", "facility_info/state": "Acre", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "adolescent_client_interview", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "0", "characteristic_three/ch3_q3": "0", "_uuid": "bd18e938-8cb7-4a99-aa6d-35b05ae942f1", "characteristic_three/ch3_q4": "1", "facility_info/interviewer": "Hwwk", "respondent_dem/highest_study": "Primary school", "formhub/uuid": "933bba82422444eda5c4d05d39f73684", "characteristic_one/ch1_q2": "1", "characteristic_one/ch1_q1": "1", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/reporting_period": "2014-02-06", "facility_info/interview_date": "2014-02-06", "_id": 24651}',  # noqa

        # clinic.id = 2 submissions        '{"facility_info/facility_cnes": "1A2B", "facility_info/municipality": "Brasilia", "facility_info/state": "Acre", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "male", "_xform_id_string": "health_care_provider_interview", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "0", "characteristic_three/ch3_q3": "0", "_uuid": "ac18e938-8cb7-4a99-aa6d-35b05ae942d3", "characteristic_three/ch3_q4": "1", "facility_info/interviewer": "Hask", "respondent_dem/highest_study": "College", "formhub/uuid": "873bba82422444eda5c4d05d39f73616", "characteristic_one/ch1_q1": "1", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/reporting_period": "2014-02-06", "facility_info/interview_date": "2014-02-06", "_id": 24651}',  # noqa

        '{"facility_info/facility_cnes": "3E4G", "facility_info/municipality": "Brasilia", "facility_info/state": "Acre", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "male", "_xform_id_string": "adolescent_client_interview", "respondent_dem/study_yes_Esp": "Yes", "_geolocation": ["-1.2988671", "36.7906039"], "respondent_dem/res_age": "18", "facility_info/facility_geopoint": "-1.2988671 36.7906039 0.0 34.208", "meta/instanceID": "uuid:a795726b-9989-4c70-ad92-93eb2c460b57", "_status": "submitted_via_web", "facility_info/HS_char": "twenty", "respondent_dem/study": "yes", "respondent_dem/marital_status": "single", "characteristic_twenty/ch20_q1": "1", "_uuid": "a795726b-9989-4c70-ad92-93eb2c460b57", "facility_info/interviewer": "Larry Weya", "respondent_dem/highest_study": "High school", "formhub/uuid": "dccae423c9704aa283b4a10343c916c9", "_submission_time": "2014-02-04T06:22:32", "_attachments": [], "facility_info/reporting_period": "2014-02-06", "facility_info/interview_date": "2014-02-03", "_id": 23936}',  # noqa
        '{"facility_info/facility_cnes": "3E4G", "facility_info/municipality": "Brasilia", "facility_info/state": "Acre", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "adolescent_client_interview", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "0", "characteristic_three/ch3_q3": "0", "_uuid": "ac18e938-8cb7-4a99-aa6d-35b05ae942d3", "characteristic_three/ch3_q4": "1", "facility_info/interviewer": "Hask", "respondent_dem/highest_study": "College", "formhub/uuid": "873bba82422444eda5c4d05d39f73616", "characteristic_one/ch1_q2": "0", "characteristic_one/ch1_q1": "1", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/reporting_period": "2014-02-06", "facility_info/interview_date": "2014-02-06", "_id": 24651}',  # noqa
        # non existent clinic id
        '{"facility_info/facility_cnes": "no-such-clinic", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "male", "_xform_id_string": "health_care_provider_interview", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "0", "characteristic_three/ch3_q3": "0", "_uuid": "ac18e938-8cb7-4a99-aa6d-35b05ae942d3", "characteristic_three/ch3_q4": "1", "facility_info/interviewer": "Hask", "respondent_dem/highest_study": "College", "formhub/uuid": "873bba82422444eda5c4d05d39f73616", "characteristic_one/ch1_q1": "1", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/reporting_period": "2014-02-06", "facility_info/interview_date": "2014-02-06", "_id": 24651}'  # noqa
    ]
    clinic_registrations = [
        '{"facility_info/facility_cnes": "1A2B", "facility_info/municipality": "Brasilia", "facility_info/state": "Acre", "_notes": [], "_id": 27761, "user_id": "2", "_submission_time": "2014-02-20T09:24:40", "_uuid": "a3814ab2-6fcc-472b-9a7c-450d92b4fb10", "_bamboo_dataset_id": "", "_tags": [], "_attachments": [], "_geolocation": [null, null], "_xform_id_string": "clinic_registration", "_status": "submitted_via_web", "meta/instanceID": "uuid:a3814ab2-6fcc-472b-9a7c-450d92b4fb10", "facility_info/facility_name": "New Kakamega Clinic", "formhub/uuid": "4796cf1b830840b0a326cc16eda45083"}',  # noqa
        # bad user id
        '{"facility_info/facility_cnes": "3E4G", "facility_info/municipality": "Brasilia", "facility_info/state": "Acre", "_notes": [], "_id": 27761, "user_id": "-1", "_submission_time": "2014-02-20T09:24:40", "_uuid": "a3814ab2-6fcc-472b-9a7c-450d92b4fb10", "_bamboo_dataset_id": "", "_tags": [], "_attachments": [], "_geolocation": [null, null], "_xform_id_string": "clinic_registration", "_status": "submitted_via_web", "meta/instanceID": "uuid:a3814ab2-6fcc-472b-9a7c-450d92b4fb10", "facility_info/facility_name": "New Kakamega Clinic", "formhub/uuid": "4796cf1b830840b0a326cc16eda45083"}'  # noqa
    ]

    brazil_submissions = [
        # clinic.id = 1
        '{"facility_info/facility_cnes": "1A2B", "facility_info/municipality": "Brasilia", "facility_info/state": "Acre", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "male", "_xform_id_string": "health_care_provider_interview", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "999", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "0", "characteristic_three/ch3_q3": "0", "_uuid": "ac18e938-8cb7-4a99-aa6d-35b05ae942d3", "characteristic_three/ch3_q4": "1", "facility_info/interviewer": "Hask", "respondent_dem/highest_study": "College", "formhub/uuid": "873bba82422444eda5c4d05d39f73616", "characteristic_one/ch1_q1": "1", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/reporting_period": "2014-02-06", "facility_info/interview_date": "2014-02-06", "_id": 24651}',  # noqa
        '{"facility_info/facility_cnes": "1A2B", "facility_info/municipality": "Brasilia", "facility_info/state": "Acre", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "adolescent_client_interview", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "999", "characteristic_three/ch3_q3": "0", "_uuid": "af18e938-8cb7-4a99-aa6d-35b05ae942d2", "characteristic_three/ch3_q4": "0", "facility_info/interviewer": "Kwhba", "respondent_dem/highest_study": "High school", "formhub/uuid": "753bba82422444eda5c4d05d39f73667", "characteristic_one/ch1_q2": "1", "characteristic_one/ch1_q1": "0", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/reporting_period": "2014-02-06", "facility_info/interview_date": "2014-02-06", "_id": 24651}',  # noqa
        '{"facility_info/facility_cnes": "1A2B", "facility_info/municipality": "Brasilia", "facility_info/state": "Acre", "_notes": [], "_bamboo_dataset_id": "", "_tags": [], "respondent_dem/respondent_sex": "female", "_xform_id_string": "adolescent_client_interview", "respondent_dem/study_yes_Esp": "Yes", "characteristic_one/ch1_q1_yes": "A lot of patients", "respondent_dem/res_age": "17", "facility_info/facility_geopoint": "-1.2988326 36.7906152 0.0 31.12", "meta/instanceID": "uuid:af18e938-8cb7-4a99-aa6d-35b05ae942d2", "_geolocation": ["-1.2988326", "36.7906152"], "_status": "submitted_via_web", "facility_info/HS_char": "one three", "respondent_dem/study": "yes", "characteristic_three/ch3_q1": "1", "respondent_dem/marital_status": "married", "characteristic_three/ch3_q2": "0", "characteristic_three/ch3_q3": "0", "_uuid": "bd18e938-8cb7-4a99-aa6d-35b05ae942f1", "characteristic_three/ch3_q4": "1", "facility_info/interviewer": "Hwwk", "respondent_dem/highest_study": "Primary school", "formhub/uuid": "933bba82422444eda5c4d05d39f73684", "characteristic_one/ch1_q2": "1", "characteristic_one/ch1_q1": "1", "_submission_time": "2014-02-06T08:56:02", "_attachments": [], "facility_info/reporting_period": "2014-02-06", "facility_info/interview_date": "2014-02-06", "_id": 24651}',  # noqa
    ]

    adolescent_client_submissions = [
        '{"characteristic_nine/ch9_invalid": "0", "subscriber_id": "no subscriberid property in enketo", "_tags": [], "characteristic_eight/ch8_score": "0", "characteristic_six/ch6_score": "1", "characteristic_thirteen/ch13_score": "2", "_xform_id_string": "adolescent_client_interview", "characteristic_thirteen/ch13_q1/ch13_q1e": "0", "characteristic_thirteen/ch13_q1/ch13_q1d": "1", "characteristic_fourteen/ch14_invalid": "1", "characteristic_thirteen/ch13_q1/ch13_q1a": "1", "characteristic_thirteen/ch13_q1/ch13_q1c": "0", "characteristic_thirteen/ch13_q1/ch13_q1b": "0", "characteristic_three/ch3_invalid": "0", "facility_info/facility_cnes": "0010731", "characteristic_ten/ch10_score": "4", "characteristic_fourteen/ch14_q2": "0", "start_time": "2015-03-13T14:25:49.000+03:00", "characteristic_three/ch3_q1": "pessoal_da_administracao", "characteristic_fourteen/ch14_q6": "0", "characteristic_seventeen/ch17_score": "NaN", "facility_info/state": "distrito_federal", "characteristic_seven/ch7_invalid": "0", "characteristic_twelve/ch12_invalid": "0", "resp_demographics/resp_sex": "male", "terminate_int9": "0", "terminate_int8": "0", "terminate_int7": "0", "_submission_time": "2015-03-13T12:06:57", "terminate_int5": "0", "terminate_int4": "0", "terminate_int3": "0", "terminate_int2": "0", "_geolocation": [null, null], "characteristic_eleven/ch11_q1": "1", "characteristic_eleven/ch11_q2": "00", "characteristic_eleven/ch11_q3": "1", "characteristic_sixteen/ch16_invalid": "0", "characteristic_nine/ch9_q2/ch9_q2b": "0", "characteristic_nine/ch9_q2/ch9_q2c": "1", "characteristic_nine/ch9_q2/ch9_q2a": "0", "total_invalid8": "2", "total_invalid9": "2", "facility_info/municipality": "brasilia", "total_invalid2": "0", "meta/instanceID": "uuid:42006843-79da-472e-ae83-eadb021119e5", "total_invalid4": "0", "total_invalid5": "1", "total_invalid6": "1", "total_invalid7": "1", "characteristic_five/ch5_q1": "1", "characteristic_nineteen/ch19_score": "1", "characteristic_six/ch6_q2": "Fliers", "characteristic_six/ch6_q1": "1", "characteristic_one/ch1_invalid": "0", "characteristic_twenty/ch20_q1": "1", "facility_info/HS_char": "one two three five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen nineteen twenty", "end_time": "2015-03-13T15:06:56.000+03:00", "phone_number": "no phonenumber property in enketo", "characteristic_seven/ch7_score": "2", "characteristic_one/ch1_score": "1", "facility_info/reporting_period": "1may_31jul_2015", "_uuid": "42006843-79da-472e-ae83-eadb021119e5", "characteristic_eleven/ch11_score": "2", "characteristic_two/ch2_q1": "1", "_version": "201503121224", "characteristic_five/ch5_score": "1", "terminate_int6": "0", "resp_demographics/resp_in_school": "no", "_notes": [], "resp_demographics/resp_age": 18, "terminate_int": "0", "characteristic_fifteen/ch15_score": "0", "_bamboo_dataset_id": "", "characteristic_three/ch3_score": "1", "characteristic_fifteen/ch15_invalid": "0", "characteristic_five/ch5_invalid": "0", "terminate_int10": "0", "characteristic_ten/ch10_q2": "1", "characteristic_ten/ch10_q3": "1", "characteristic_ten/ch10_q1": "1", "characteristic_ten/ch10_q4": "1", "characteristic_nineteen/ch19_invalid": "0", "characteristic_twelve/ch12_score": "0", "_status": "submitted_via_web", "characteristic_nine/ch9_q1/ch9_q1c": "0", "characteristic_seven/ch7_q3": "1", "characteristic_seven/ch7_q2": "1", "characteristic_seven/ch7_q1": "0", "characteristic_twelve/ch12_q1": "0", "characteristic_twelve/ch12_q3": "0", "characteristic_twelve/ch12_q2": "0", "resp_demographics/resp_marital_status": "boyfriend_girlfriend", "characteristic_fifteen/ch15_q2": "0", "characteristic_fifteen/ch15_q1": "0", "characteristic_eight/ch8_invalid": "0", "characteristic_one/ch1_q2": "0", "characteristic_one/ch1_q1": "1", "characteristic_nineteen/ch19_q1": "1", "characteristic_nineteen/ch19_q2": "0", "characteristic_twenty/ch20_score": "1", "total_invalid": "0", "characteristic_six/ch6_invalid": "0", "characteristic_ten/ch10_invalid": "0", "characteristic_eight/ch8_q1": "0", "characteristic_sixteen/ch16_score": "1", "total_invalid3": "0", "characteristic_twenty/ch20_invalid": "0", "sim_serial": "no simserial property in enketo", "_duration": 2467.0, "characteristic_nine/ch9_score": "2", "total_invalid10": "2", "characteristic_fourteen/ch14_q1": "1", "characteristic_seventeen/ch17_invalid": "1", "characteristic_two/ch2_score": "1", "characteristic_two/ch2_invalid": "0", "characteristic_thirteen/ch13_invalid": "0", "characteristic_nine/ch9_q1/ch9_q1a": "1", "characteristic_nine/ch9_q1/ch9_q1b": "0", "formhub/uuid": "89f76ed6137d4d1f8986e6c1f2d30603", "characteristic_fourteen/ch14_score": "NaN", "_attachments": [], "characteristic_eleven/ch11_invalid": "0", "_submitted_by": null, "characteristic_sixteen/ch16_q1": "0", "device_id": "localhost:cOUuftC4kZnkSPZs", "characteristic_sixteen/ch16_q2": "1", "_id": 309, "facility_info/interviewer_name": "Geoffrey Muchai"}',  # noqa
        '{"characteristic_nine/ch9_invalid":"0","subscriber_id":"no subscriberid property in enketo","_tags":[],"characteristic_eight/ch8_score":"1","characteristic_six/ch6_score":"1","characteristic_thirteen/ch13_score":"5","_xform_id_string":"adolescent_client_interview","characteristic_thirteen/ch13_q1/ch13_q1e":"1","characteristic_thirteen/ch13_q1/ch13_q1d":"1","characteristic_fourteen/ch14_invalid":"0","characteristic_thirteen/ch13_q1/ch13_q1a":"1","characteristic_thirteen/ch13_q1/ch13_q1c":"1","characteristic_thirteen/ch13_q1/ch13_q1b":"1","characteristic_three/ch3_invalid":"0","facility_info/facility_cnes":"0010731","characteristic_ten/ch10_score":"0","characteristic_fourteen/ch14_q2":"1","characteristic_fourteen/ch14_q3":"1","start_time":"2015-03-13T15:08:58.000+03:00","characteristic_three/ch3_q1":"recepcionista","characteristic_seventeen/ch17_invalid":"1","characteristic_fourteen/ch14_q4":"1","characteristic_fourteen/ch14_q5":"1","characteristic_seventeen/ch17_score":"NaN","facility_info/state":"distrito_federal","characteristic_seven/ch7_invalid":"0","characteristic_twelve/ch12_invalid":"0","resp_demographics/resp_sex":"male","terminate_int9":"0","terminate_int8":"0","terminate_int7":"0","_submission_time":"2015-03-13T12:30:12","terminate_int5":"0","terminate_int4":"0","terminate_int3":"0","terminate_int2":"0","_geolocation":[null,null],"characteristic_eleven/ch11_q1":"1","characteristic_eleven/ch11_q2":"1","characteristic_eleven/ch11_q3":"1","characteristic_sixteen/ch16_invalid":"0","characteristic_nine/ch9_q2/ch9_q2b":"1","characteristic_nine/ch9_q2/ch9_q2c":"1","characteristic_nine/ch9_q2/ch9_q2a":"1","total_invalid8":"1","total_invalid9":"1","facility_info/municipality":"brasilia","total_invalid2":"0","meta/instanceID":"uuid:0736cff4-a0e7-4510-bb34-8d124776ea76","total_invalid4":"0","total_invalid5":"0","total_invalid6":"0","total_invalid7":"0","characteristic_five/ch5_q1":"1","characteristic_nineteen/ch19_score":"2","characteristic_six/ch6_q2":"TV","characteristic_six/ch6_q1":"1","characteristic_one/ch1_invalid":"0","facility_info/reporting_period":"1may_31jul_2015","facility_info/HS_char":"one two three five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen nineteen twenty","end_time":"2015-03-13T15:30:12.000+03:00","phone_number":"no phonenumber property in enketo","characteristic_seven/ch7_score":"2","characteristic_one/ch1_score":"1","characteristic_twenty/ch20_q1":"1","_uuid":"0736cff4-a0e7-4510-bb34-8d124776ea76","characteristic_eleven/ch11_score":"3","characteristic_two/ch2_q1":"1","_version":"201503121224","characteristic_five/ch5_score":"1","terminate_int6":"0","resp_demographics/resp_in_school":"no","_notes":[],"resp_demographics/resp_age":16,"terminate_int":"0","characteristic_fifteen/ch15_score":"2","_bamboo_dataset_id":"","characteristic_three/ch3_score":"1","characteristic_fifteen/ch15_invalid":"0","characteristic_five/ch5_invalid":"0","terminate_int10":"0","characteristic_ten/ch10_q2":"0","characteristic_ten/ch10_q3":"0","characteristic_ten/ch10_q1":"0","characteristic_ten/ch10_q4":"0","characteristic_nineteen/ch19_invalid":"0","characteristic_twelve/ch12_score":"3","_status":"submitted_via_web","characteristic_nine/ch9_q1/ch9_q1c":"1","characteristic_seven/ch7_q3":"1","characteristic_seven/ch7_q2":"0","characteristic_seven/ch7_q1":"1","characteristic_twelve/ch12_q1":"1","characteristic_twelve/ch12_q3":"1","characteristic_twelve/ch12_q2":"1","resp_demographics/resp_marital_status":"single","characteristic_fifteen/ch15_q2":"1","characteristic_fifteen/ch15_q1":"1","characteristic_eight/ch8_invalid":"0","characteristic_one/ch1_q2":"0","characteristic_one/ch1_q1":"1","characteristic_nineteen/ch19_q1":"1","characteristic_nineteen/ch19_q2":"1","characteristic_twenty/ch20_score":"1","total_invalid":"0","characteristic_six/ch6_invalid":"0","characteristic_ten/ch10_invalid":"0","characteristic_eight/ch8_q1":"1","characteristic_sixteen/ch16_score":"2","total_invalid3":"0","characteristic_twenty/ch20_invalid":"0","sim_serial":"no simserial property in enketo","_duration":1274,"characteristic_nine/ch9_score":"6","total_invalid10":"1","characteristic_fourteen/ch14_q1":"1","characteristic_fourteen/ch14_q6":"1","characteristic_two/ch2_score":"1","characteristic_two/ch2_invalid":"0","characteristic_thirteen/ch13_invalid":"0","characteristic_nine/ch9_q1/ch9_q1a":"1","characteristic_nine/ch9_q1/ch9_q1b":"1","formhub/uuid":"89f76ed6137d4d1f8986e6c1f2d30603","characteristic_fourteen/ch14_score":"6","_attachments":[],"characteristic_eleven/ch11_invalid":"0","_submitted_by":null,"characteristic_sixteen/ch16_q1":"1","device_id":"localhost:cOUuftC4kZnkSPZs","characteristic_sixteen/ch16_q2":"1","_id":310,"facility_info/interviewer_name":"Geof"}',  # noqa
        '{"characteristic_nine/ch9_invalid":"0","subscriber_id":"no subscriberid property in enketo","_tags":[],"characteristic_eight/ch8_score":"0","characteristic_six/ch6_score":"0","characteristic_thirteen/ch13_score":"0","_xform_id_string":"adolescent_client_interview","characteristic_thirteen/ch13_q1/ch13_q1e":"0","characteristic_thirteen/ch13_q1/ch13_q1d":"0","characteristic_fourteen/ch14_invalid":"0","characteristic_thirteen/ch13_q1/ch13_q1a":"0","characteristic_thirteen/ch13_q1/ch13_q1c":"0","characteristic_thirteen/ch13_q1/ch13_q1b":"0","characteristic_three/ch3_invalid":"0","facility_info/facility_cnes":"0010731","characteristic_ten/ch10_score":"4","characteristic_fourteen/ch14_q2":"0","characteristic_fourteen/ch14_q3":"0","start_time":"2015-03-13T15:32:14.000+03:00","characteristic_three/ch3_q1":"pessoal_da_administracao","characteristic_seventeen/ch17_invalid":"1","characteristic_fourteen/ch14_q4":"0","characteristic_fourteen/ch14_q5":"0","characteristic_seventeen/ch17_score":"NaN","facility_info/state":"distrito_federal","characteristic_seven/ch7_invalid":"0","characteristic_twelve/ch12_invalid":"0","resp_demographics/resp_sex":"female","terminate_int9":"0","terminate_int8":"0","terminate_int7":"0","terminate_int6":"0","terminate_int5":"0","terminate_int4":"0","terminate_int3":"0","terminate_int2":"0","_geolocation":[null,null],"characteristic_eleven/ch11_q1":"0","characteristic_eleven/ch11_q2":"0","characteristic_eleven/ch11_q3":"0","characteristic_sixteen/ch16_invalid":"0","characteristic_nine/ch9_q2/ch9_q2b":"0","characteristic_nine/ch9_q2/ch9_q2c":"0","characteristic_nine/ch9_q2/ch9_q2a":"0","total_invalid8":"1","total_invalid9":"1","facility_info/municipality":"brasilia","total_invalid2":"0","meta/instanceID":"uuid:7f028d33-3ab0-4518-8f54-0e70abbd8adf","total_invalid4":"0","total_invalid5":"0","total_invalid6":"0","total_invalid7":"0","characteristic_five/ch5_q1":"0","characteristic_nineteen/ch19_score":"0","characteristic_six/ch6_q2":"bla bla bla","characteristic_six/ch6_q1":"0","characteristic_one/ch1_invalid":"0","facility_info/reporting_period":"1may_31jul_2015","facility_info/HS_char":"one two three five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen nineteen twenty","end_time":"2015-03-13T15:40:29.000+03:00","phone_number":"no phonenumber property in enketo","characteristic_seven/ch7_score":"1","characteristic_one/ch1_score":"2","characteristic_twenty/ch20_q1":"0","_uuid":"7f028d33-3ab0-4518-8f54-0e70abbd8adf","characteristic_eleven/ch11_score":"0","characteristic_two/ch2_q1":"0","_version":"201503121224","characteristic_five/ch5_score":"0","resp_demographics/resp_in_school":"yes","_notes":[],"resp_demographics/resp_age":16,"terminate_int":"0","characteristic_fifteen/ch15_score":"0","_bamboo_dataset_id":"","characteristic_three/ch3_score":"1","characteristic_fifteen/ch15_invalid":"0","characteristic_five/ch5_invalid":"0","terminate_int10":"0","characteristic_ten/ch10_q2":"1","characteristic_ten/ch10_q3":"1","characteristic_ten/ch10_q1":"1","characteristic_ten/ch10_q4":"1","characteristic_nineteen/ch19_invalid":"0","characteristic_twelve/ch12_score":"0","_status":"submitted_via_web","characteristic_nine/ch9_q1/ch9_q1c":"0","characteristic_seven/ch7_q3":"0","characteristic_seven/ch7_q2":"1","characteristic_seven/ch7_q1":"0","characteristic_twelve/ch12_q1":"0","characteristic_twelve/ch12_q3":"0","characteristic_twelve/ch12_q2":"0","resp_demographics/resp_marital_status":"live_together","characteristic_fifteen/ch15_q2":"0","characteristic_fifteen/ch15_q1":"0","characteristic_eight/ch8_invalid":"0","characteristic_one/ch1_q2":"1","characteristic_one/ch1_q1":"1","characteristic_nineteen/ch19_q1":"0","characteristic_nineteen/ch19_q2":"0","characteristic_twenty/ch20_score":"0","total_invalid":"0","characteristic_six/ch6_invalid":"0","characteristic_ten/ch10_invalid":"0","characteristic_eight/ch8_q1":"0","characteristic_sixteen/ch16_score":"0","total_invalid3":"0","characteristic_twenty/ch20_invalid":"0","sim_serial":"no simserial property in enketo","_duration":495,"characteristic_nine/ch9_score":"0","total_invalid10":"1","characteristic_fourteen/ch14_q1":"0","characteristic_fourteen/ch14_q6":"0","characteristic_two/ch2_score":"0","characteristic_two/ch2_invalid":"0","resp_demographics/resp_in_school_yes":"ensino_superior","characteristic_thirteen/ch13_invalid":"0","characteristic_nine/ch9_q1/ch9_q1a":"0","characteristic_nine/ch9_q1/ch9_q1b":"0","formhub/uuid":"89f76ed6137d4d1f8986e6c1f2d30603","_submission_time":"2015-03-13T12:40:29","characteristic_fourteen/ch14_score":"0","_attachments":[],"characteristic_eleven/ch11_invalid":"0","_submitted_by":null,"characteristic_sixteen/ch16_q1":"0","device_id":"localhost:cOUuftC4kZnkSPZs","characteristic_sixteen/ch16_q2":"0","_id":311,"facility_info/interviewer_name":"Anita"}',  # noqa
        '{"characteristic_nine/ch9_invalid":"0","subscriber_id":"no subscriberid property in enketo","_tags":[],"characteristic_eight/ch8_score":"00","characteristic_six/ch6_score":"00","characteristic_thirteen/ch13_score":"0","_xform_id_string":"adolescent_client_interview","characteristic_thirteen/ch13_q1/ch13_q1e":"00","characteristic_thirteen/ch13_q1/ch13_q1d":"0","characteristic_fourteen/ch14_invalid":"0","characteristic_thirteen/ch13_q1/ch13_q1a":"00","characteristic_thirteen/ch13_q1/ch13_q1c":"00","characteristic_thirteen/ch13_q1/ch13_q1b":"00","characteristic_three/ch3_invalid":"0","facility_info/facility_cnes":"0010731","characteristic_ten/ch10_score":"NaN","characteristic_fourteen/ch14_q2":"00","characteristic_fourteen/ch14_q3":"00","start_time":"2015-03-16T15:36:16.000+03:00","characteristic_three/ch3_q1":"pessoal_da_administracao","characteristic_seventeen/ch17_invalid":"1","characteristic_fourteen/ch14_q4":"00","characteristic_fourteen/ch14_q5":"00","characteristic_seventeen/ch17_score":"NaN","facility_info/state":"distrito_federal","characteristic_seven/ch7_invalid":"0","characteristic_twelve/ch12_invalid":"0","resp_demographics/resp_sex":"male","terminate_int9":"0","terminate_int8":"0","terminate_int7":"0","_submission_time":"2015-03-16T13:23:47","terminate_int5":"0","terminate_int4":"0","terminate_int3":"0","terminate_int2":"0","_geolocation":[null,null],"characteristic_eleven/ch11_q1":"00","characteristic_eleven/ch11_q2":"00","characteristic_eleven/ch11_q3":"00","characteristic_sixteen/ch16_invalid":"0","characteristic_nine/ch9_q2/ch9_q2b":"00","characteristic_nine/ch9_q2/ch9_q2c":"00","characteristic_nine/ch9_q2/ch9_q2a":"00","total_invalid8":"2","total_invalid9":"2","facility_info/municipality":"brasilia","total_invalid2":"1","meta/instanceID":"uuid:f1f1256d-a12d-4cca-9bd3-f3e32ced5f5f","total_invalid4":"1","total_invalid5":"1","total_invalid6":"1","total_invalid7":"1","characteristic_five/ch5_q1":"00","characteristic_nineteen/ch19_score":"0","characteristic_six/ch6_q2":"DUNNO","characteristic_six/ch6_q1":"00","characteristic_one/ch1_invalid":"0","facility_info/reporting_period":"1aug_31oct_2015","facility_info/HS_char":"one two three five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen nineteen twenty","end_time":"2015-03-16T16:23:46.000+03:00","phone_number":"no phonenumber property in enketo","characteristic_seven/ch7_score":"0","characteristic_one/ch1_score":"0","characteristic_twenty/ch20_q1":"00","_uuid":"f1f1256d-a12d-4cca-9bd3-f3e32ced5f5f","characteristic_eleven/ch11_score":"0","characteristic_two/ch2_q1":"00","_version":"201503121224","characteristic_five/ch5_score":"00","terminate_int6":"0","resp_demographics/resp_in_school":"no","_notes":[],"resp_demographics/resp_age":17,"terminate_int":"0","characteristic_fifteen/ch15_score":"0","_bamboo_dataset_id":"","characteristic_three/ch3_score":"1","characteristic_fifteen/ch15_invalid":"0","characteristic_five/ch5_invalid":"0","terminate_int10":"0","characteristic_ten/ch10_q2":"00","characteristic_ten/ch10_q3":"na","characteristic_ten/ch10_q1":"00","characteristic_ten/ch10_q4":"00","characteristic_nineteen/ch19_invalid":"0","characteristic_twelve/ch12_score":"0","_status":"submitted_via_web","characteristic_nine/ch9_q1/ch9_q1c":"00","characteristic_seven/ch7_q3":"00","characteristic_seven/ch7_q2":"00","characteristic_seven/ch7_q1":"00","characteristic_twelve/ch12_q1":"00","characteristic_twelve/ch12_q3":"00","characteristic_twelve/ch12_q2":"00","resp_demographics/resp_marital_status":"single","characteristic_fifteen/ch15_q2":"00","characteristic_fifteen/ch15_q1":"00","characteristic_eight/ch8_invalid":"0","characteristic_one/ch1_q2":"00","characteristic_one/ch1_q1":"00","characteristic_nineteen/ch19_q1":"00","characteristic_nineteen/ch19_q2":"00","characteristic_twenty/ch20_score":"00","total_invalid":"1","characteristic_six/ch6_invalid":"0","characteristic_ten/ch10_invalid":"1","characteristic_eight/ch8_q1":"00","characteristic_sixteen/ch16_score":"0","total_invalid3":"1","characteristic_twenty/ch20_invalid":"0","sim_serial":"no simserial property in enketo","_duration":2850,"characteristic_nine/ch9_score":"0","total_invalid10":"2","characteristic_fourteen/ch14_q1":"00","characteristic_fourteen/ch14_q6":"00","characteristic_two/ch2_score":"00","characteristic_two/ch2_invalid":"0","characteristic_thirteen/ch13_invalid":"0","characteristic_nine/ch9_q1/ch9_q1a":"00","characteristic_nine/ch9_q1/ch9_q1b":"00","formhub/uuid":"89f76ed6137d4d1f8986e6c1f2d30603","characteristic_fourteen/ch14_score":"0","_attachments":[],"characteristic_eleven/ch11_invalid":"0","_submitted_by":null,"characteristic_sixteen/ch16_q1":"00","device_id":"localhost:cOUuftC4kZnkSPZs","characteristic_sixteen/ch16_q2":"00","_id":312,"facility_info/interviewer_name":"Okal"}'  # noqa
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

    def _create_user(self, username):
        user_group = Group(name="user")

        user = User()
        user.group = user_group

        ona_user = OnaUser(username=username,
                           user=user,
                           refresh_token="1239khyackas")

        with transaction.manager:
            DBSession.add(ona_user)

    def _create_municipality(self, name="Test Municipality"):
        municipality = Municipality(name=name)

        with transaction.manager:
            DBSession.add(municipality)

    def setup_test_data(self):
        su_group = Group(name=groups.SUPER_USER)
        clinic_managers_group = Group(name=groups.MUNICIPALITY_MANAGER)

        su = User()
        user_setting = UserSettings(user=su)

        su_ona_user = OnaUser(
            user=su, username='super', refresh_token="a123f4")
        su.group = su_group

        manager_a = User()
        manager_a_ona_user = OnaUser(
            user=manager_a, username='manager_a', refresh_token="b345d6")
        manager_a.group = clinic_managers_group

        manager_b = User()
        manager_b_ona_user = OnaUser(
            user=manager_b, username='manager_b', refresh_token="c563e9")
        manager_b.group = clinic_managers_group

        # add a couple of clinics
        clinic1 = Clinic(id=1, name="Clinic A", code="1A2B")
        # assign a su to clinic1
        manager_a.clinics.append(clinic1)

        clinic2 = Clinic(id=2, name="Clinic B", code="3E4G")

        clinic3 = Clinic(id=3, name="Health Centre 09", code="0010731")

        reporting_period = ReportingPeriod(
            title='Period 1',
            start_date=datetime.datetime(2014, 3, 1),
            end_date=datetime.datetime(2015, 3, 1))

        with transaction.manager:
            DBSession.add_all(
                [user_setting, su_ona_user, manager_a_ona_user,
                 manager_b_ona_user, clinic1, clinic2, clinic3,
                 reporting_period])

    def create_submissions(self):
        # make submissions
        for i in range(6):
            Submission.create_from_json(self.submissions[i])
        transaction.commit()

    def create_brazil_submissions(self):
        # make submissions
        for i in range(3):
            Submission.create_from_json(self.brazil_submissions[i])
        transaction.commit()

    def create_adolescent_client_submissions(self):
        # make submissions
        for i in range(len(self.adolescent_client_submissions)):
            Submission.create_from_json(self.adolescent_client_submissions[i])
        transaction.commit()


class IntegrationTestBase(TestBase):
    def setUp(self):
        super(IntegrationTestBase, self).setUp()
        pwd_context.load_path('test.ini')
        # configure enketo
        enketo.configure(settings['enketo_url'], settings['enketo_api_token'])
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
        current_dir = os.getcwd()
        app = main(
            {
                '__file__': os.path.join(current_dir, SETTINGS_FILE),
                'here': current_dir
            },
            **settings)
        self.testapp = TestApp(app, extra_environ={
            'HTTP_HOST': 'example.com'
        })
        self.request = testing.DummyRequest()
        # used by cookie auth as the domain
        self.request.environ = {
            'SERVER_NAME': 'example.com',
        }
