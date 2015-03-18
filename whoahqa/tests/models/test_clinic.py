import datetime
import json

from whoahqa.constants import characteristics as constants
from whoahqa.constants import brazil_characteristics as brazil_constants
from whoahqa.models import (
    DBSession,
    OnaUser,
    Clinic,
    ReportingPeriod,
    ClinicCharacteristics
)
from whoahqa.tests import TestBase


class TestClinic(TestBase):

    def test_assign_to_user(self):
        self.setup_test_data()
        user = OnaUser.get(OnaUser.username == 'manager_a').user
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

    def test_filter_clinics(self):
        self.setup_test_data()

        clinics = Clinic.filter_clinics("Clinic B", True)
        self.assertGreater(len(clinics), 0)

    def test_get_num_responses_per_characteristic_xform_id(self):
        self.setup_test_data()
        self.create_submissions()
        clinic_a = Clinic.get(Clinic.name == 'Clinic A')
        result = clinic_a.get_num_responses_per_characteristic_xform_id(
            clinic_a.id)
        self.assertEqual(len(result), 5)
        self.assertIn(
            {'count': 1, 'characteristic': constants.TWENTY,
             'xform_id': constants.HEALTH_FACILITY_MANAGER},
            result)
        self.assertIn(
            {'count': 1, 'characteristic': constants.THREE,
             'xform_id': constants.HEALTH_CARE_PROVIDER},
            result)
        self.assertIn(
            {'count': 2, 'characteristic': constants.THREE,
             'xform_id': constants.ADOLESCENT_CLIENT},
            result)
        self.assertIn(
            {'count': 1, 'characteristic': constants.ONE,
             'xform_id': constants.HEALTH_CARE_PROVIDER},
            result)
        self.assertIn(
            {'count': 2, 'characteristic': constants.ONE,
             'xform_id': constants.ADOLESCENT_CLIENT},
            result)

    def test_calculate_aggregate_scores(self):
        clinic = Clinic(code="123", name="Test Clinic")
        characteristic_one = constants.CHARACTERISTIC_MAPPING[constants.ONE]
        score_xpath = characteristic_one.keys()[0]
        num_responses = 3
        submissions = [json.loads(s) for s in self.submissions[1: 4]]
        scores = clinic.calculate_characteristic_aggregate_scores(
            score_xpath, num_responses, submissions)
        self.assertIsInstance(scores, float)
        self.assertEqual(scores, 1.3333333333333333)

    def test_calculate_aggregate_scores_raises_value_error_for_0_submissions(
            self):
        clinic = Clinic(code="123", name="Test Clinic")
        characteristic_one = constants.CHARACTERISTIC_MAPPING[constants.ONE]
        score_xpath = characteristic_one.keys()[0]
        num_responses = 0
        submissions = [json.loads(s) for s in self.submissions[1: 4]]
        self.assertRaises(
            ValueError, clinic.calculate_characteristic_aggregate_scores,
            score_xpath, num_responses, submissions)

    def test_get_period_submissions(self):
        self.setup_test_data()
        self.create_submissions()
        clinic = Clinic.get(Clinic.name == 'Clinic A')
        submissions = clinic.get_period_clinic_submissions()
        self.assertEqual(len(submissions), 7)

    def test_get_scores(self):
        """
        Test scores calculation for all characteristic and tool pairs per
        clinic
        """
        self.setup_test_data()
        self.create_submissions()

        clinic = Clinic.get(Clinic.id == 1)
        scores = clinic.get_scores()

        scores_1 = scores['one']
        self.assertEqual(scores_1[constants.ADOLESCENT_CLIENT], {
            'aggregate_score': 1.5,
            'num_questions': 2,
            'num_responses': 2,
            'num_pending_responses': 4,
        })
        self.assertEqual(scores_1[constants.HEALTH_CARE_PROVIDER], {
            'aggregate_score': 1,
            'num_questions': 1,
            'num_responses': 1,
            'num_pending_responses': 4,
        })

        self.assertEqual(scores_1['totals'], {
            'total_scores': 2.5,
            'total_questions': 5,
            'total_responses': 3,
            'total_percentage': 50.0,
            'meets_threshold': False,
            'score_classification': constants.BAD
        })

    def test_get_scores_when_no_responses_sets_totals_to_none(self):
        self.setup_test_data()
        self.create_submissions()

        clinic = Clinic.get(Clinic.id == 1)
        scores = clinic.get_scores()

        scores_10 = scores['ten']
        self.assertEqual(scores_10[constants.ADOLESCENT_CLIENT], {
            'aggregate_score': None,
            'num_questions': 4,
            'num_responses': 0,
            'num_pending_responses': 6,
        })

        self.assertEqual(scores_10['totals'], {
            'total_scores': None,
            'total_questions': 10,
            'total_responses': 0,
            'total_percentage': None,
            'meets_threshold': False,
            'score_classification': None
        })

    def test_is_assigned_returns_true_if_assigned(self):
        self.setup_test_data()
        clinic_a = Clinic.get(Clinic.id == 1)
        self.assertTrue(clinic_a.is_assigned)

    def test_is_assigned_returns_false_if_not_assigned(self):
        self.setup_test_data()
        clinic_b = Clinic.get(Clinic.id == 2)
        self.assertFalse(clinic_b.is_assigned)

    def test_date_created_is_automatically_populated_on_create(self):
        self.setup_test_data()
        clinic_a = Clinic.get(Clinic.id == 1)
        self.assertEquals(
            clinic_a.date_created.date(), datetime.datetime.today().date())

    def test_calculate_key_indicator_scores_when_no_responses_exist(self):
        """ should return None when no responses exist
        """
        self.setup_test_data()
        clinic_a = Clinic.get(Clinic.id == 1)
        key_indicator_scores = clinic_a.calculate_key_indicator_scores(
            (constants.ONE, constants.TWO, constants.THREE))
        self.assertEqual(key_indicator_scores, {
            constants.ONE: None,
            constants.TWO: None,
            constants.THREE: None
        })

    def test_calculate_key_indicator_when_responses_exist(self):
        """ should return a valid value when responses exist
        """
        self.setup_test_data()
        self.create_submissions()
        clinic_a = Clinic.get(Clinic.id == 1)
        key_indicator_scores = clinic_a.calculate_key_indicator_scores(
            (constants.ONE, constants.TWO, constants.THREE))
        self.assertEqual(key_indicator_scores, {
            constants.ONE: 50.0,
            constants.TWO: None,
            constants.THREE: 33.33333333333333
        })

    def test_get_item_returns_reporting_period(self):
        self.setup_test_data()
        period = ReportingPeriod(
            title="2013/2014",
            start_date=datetime.datetime(2013, 3, 13),
            end_date=datetime.datetime(2014, 3, 13))
        DBSession.add(period)
        DBSession.flush()
        period = ReportingPeriod.newest()
        clinic = Clinic.newest()
        selected_period = clinic.__getitem__(period.id)
        self.assertIsInstance(selected_period, ReportingPeriod)
        self.assertEqual(selected_period, period)

    def test_raise_key_error_when_invalid_period_id(self):
        self.setup_test_data()
        clinic = Clinic.newest()
        self.assertRaises(KeyError, clinic.__getitem__, "abc")

    def test_get_active_characteristics_filters_by_period(self):
        self.setup_test_data()
        period_1 = ReportingPeriod.get(ReportingPeriod.title == 'Period 1')
        clinic_a = Clinic.get(Clinic.name == 'Clinic A')
        period2 = ReportingPeriod(
            title='Period 2',
            start_date=datetime.datetime(2014, 1, 1),
            end_date=datetime.datetime(2014, 1, 1))

        DBSession.add(period2)
        DBSession.flush()
        clinic_char1 = ClinicCharacteristics(
            clinic_id=clinic_a.id,
            characteristic_id='one',
            period_id=period_1.id)

        clinic_char2 = ClinicCharacteristics(
            clinic_id=clinic_a.id,
            characteristic_id='one',
            period_id=period2.id)

        DBSession.add_all([clinic_char1, clinic_char2])

        characteristics = clinic_a.get_active_characteristics(period_1)

        self.assertEqual(len(characteristics), 1)

    def test_calculate_key_indicator_for_brazil_responses(self):
        """ should return a valid value when responses exist
        """
        self.setup_test_data()
        self.create_brazil_submissions()
        clinic_a = Clinic.get(Clinic.id == 1)
        key_indicator_scores = clinic_a.calculate_key_indicator_scores(
            [brazil_constants.THREE])
        self.assertEqual(key_indicator_scores, {brazil_constants.THREE: 25.0})

    def test_calculate_characteristic_scores_with_period(self):
        self.setup_test_data()
        self.create_adolescent_client_submissions()
        health_centre = Clinic.get(Clinic.id == 3)

        period = '1may_31jul_2015'
        scores = health_centre.get_scores(period)

        scores_1 = scores['one']
        self.assertEqual(scores_1[constants.ADOLESCENT_CLIENT], {
            'aggregate_score': 1.3333333333333333,
            'num_questions': 2,
            'num_responses': 3,
            'num_pending_responses': 3,
        })
        self.assertEqual(scores_1[constants.HEALTH_CARE_PROVIDER], {
            'aggregate_score': None,
            'num_questions': 1,
            'num_responses': 0,
            'num_pending_responses': 5,
        })

        self.assertEqual(scores_1['totals'], {
            'total_scores': 1.3333333333333333,
            'total_questions': 5,
            'total_responses': 3,
            'total_percentage': 26.666666666666668,
            'meets_threshold': False,
            'score_classification': constants.BAD
        })

        # Test scores of characteristic with an invalid entry
        score_14 = scores['fourteen']
        self.assertEqual(score_14[constants.ADOLESCENT_CLIENT], {
            'aggregate_score': 3.0,
            'num_questions': 6,
            'num_responses': 2,
            'num_pending_responses': 4,
        })
        self.assertEqual(score_14[constants.HEALTH_FACILITY_MANAGER], {
            'aggregate_score': None,
            'num_questions': 2,
            'num_responses': 0,
            'num_pending_responses': 1,
        })

        self.assertEqual(score_14['totals'], {
            'total_scores': 3.0,
            'total_questions': 10,
            'total_responses': 2,
            'total_percentage': 30.0,
            'meets_threshold': False,
            'score_classification': constants.BAD
        })

    def test_clinic_scores_when_no_submissions_for_period(self):
        self.setup_test_data()
        self.create_adolescent_client_submissions()
        period = '1may_31jul_2015'
        clinic = Clinic.get(Clinic.id == 1)

        scores = clinic.get_scores(period)

        scores_1 = scores['one']
        self.assertEqual(scores_1[constants.ADOLESCENT_CLIENT], {
            'aggregate_score': None,
            'num_questions': 2,
            'num_responses': 0,
            'num_pending_responses': 6,
        })
        self.assertEqual(scores_1[constants.HEALTH_CARE_PROVIDER], {
            'aggregate_score': None,
            'num_questions': 1,
            'num_responses': 0,
            'num_pending_responses': 5,
        })

        self.assertEqual(scores_1['totals'], {
            'total_scores': None,
            'total_questions': 5,
            'total_responses': 0,
            'total_percentage': None,
            'meets_threshold': False,
            'score_classification': None
        })

    def test_clinic_with_submissions_from_different_periods(self):
        self.setup_test_data()
        self.create_adolescent_client_submissions()
        health_centre = Clinic.get(Clinic.id == 3)

        period = '1aug_31oct_2015'
        scores = health_centre.get_scores(period)

        scores_1 = scores['one']
        self.assertEqual(scores_1[constants.ADOLESCENT_CLIENT], {
            'aggregate_score': 0.0,
            'num_questions': 2,
            'num_responses': 1,
            'num_pending_responses': 5,
        })
        self.assertEqual(scores_1[constants.HEALTH_CARE_PROVIDER], {
            'aggregate_score': None,
            'num_questions': 1,
            'num_responses': 0,
            'num_pending_responses': 5,
        })

        self.assertEqual(scores_1['totals'], {
            'total_scores': None,
            'total_questions': 5,
            'total_responses': 1,
            'total_percentage': 0.0,
            'meets_threshold': False,
            'score_classification': constants.BAD
        })

    def test_calculate_key_indicator_scores_with_period(self):
        self.setup_test_data()
        self.create_adolescent_client_submissions()
        health_centre = Clinic.get(Clinic.id == 3)

        period = '1may_31jul_2015'
        key_indicator_scores = health_centre.get_key_indicator_scores(period)

        self.assertEqual(key_indicator_scores, {
            'accessible': 19.343434343434343,
            'equitable': 19.999999999999996,
            'acceptable': 22.222222222222225,
            'appropriate': 3.8461538461538463,
            'effective': 10.353535353535353})

    def test_key_indicator_scores_for_period_without_submissions(self):
        self.setup_test_data()
        self.create_adolescent_client_submissions()
        health_centre = Clinic.get(Clinic.id == 3)

        period = '1april_31jul_2015'
        key_indicator_scores = health_centre.get_key_indicator_scores(period)

        self.assertEqual(key_indicator_scores, {
            'accessible': 0,
            'equitable': 0,
            'acceptable': 0,
            'appropriate': 0,
            'effective': 0})
