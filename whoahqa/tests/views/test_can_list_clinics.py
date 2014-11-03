from pyramid import testing

from whoahqa.views import (
    can_list_clinics,
)
from whoahqa.tests import TestBase


class TestCanListClinics(TestBase):
    def setUp(self):
        super(TestCanListClinics, self).setUp()
        self.setup_test_data()
        self.request = testing.DummyRequest()

    def test_returns_true_if_can_list_clinics(self):
        self.config.testing_securitypolicy(
            userid='1', permissive=True)
        value = can_list_clinics(self.request)
        self.assertTrue(value)

    def test_returns_false_if_cannot_list_clinics(self):
        self.config.testing_securitypolicy(
            userid='1', permissive=False)
        value = can_list_clinics(self.request)
        self.assertFalse(value)
