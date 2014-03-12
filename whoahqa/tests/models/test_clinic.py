import transaction
import datetime

from whoahqa import constants
from whoahqa.models import (
    DBSession,
    OnaUser,
    Clinic,
    Submission,
    ReportingPeriod,
)
from whoahqa.tests import TestBase


class TestClinic(TestBase):
    def create_submissions(self):
        # make submissions
        for i in range(6):
            Submission.create_from_json(self.submissions[i])
        transaction.commit()

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

    def test_calculate_score_works(self):
        self.setup_test_data()
        self.create_submissions()

        clinic = Clinic.get(Clinic.id == 1)
        score = clinic.calculate_score(
            constants.ONE, constants.ADOLESCENT_CLIENT)
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
            'total_percentage': 50.0
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
            'total_percentage': None
        })

    def test_calculate_score_when_no_responses_returns_none(self):
        self.setup_test_data()
        self.create_submissions()

        clinic = Clinic.get(Clinic.id == 1)
        score = clinic.calculate_score(
            constants.TWO, constants.HEALTH_CARE_PROVIDER)
        self.assertEqual(score, (None, 0))

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
