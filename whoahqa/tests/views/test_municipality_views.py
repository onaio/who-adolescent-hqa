import transaction
from pyramid import testing

from whoahqa.models import (
    Clinic,
    DBSession,
    Municipality)
from whoahqa.tests.test_base import IntegrationTestBase
from whoahqa.views import MunicipalityViews


class TestMunicipalityViews(IntegrationTestBase):
    def setUp(self):
        super(TestMunicipalityViews, self).setUp()
        self.request = testing.DummyRequest()
        self.view = MunicipalityViews(self.request)

        with transaction.manager:
            municipality = Municipality(name="Brasillia")
            DBSession.add(municipality)
            for i in range(5):
                clinic = Clinic(name="Clinic {}".format(i),
                                code="{}BCDE".format(i),
                                municipality=municipality)
                DBSession.add(clinic)

    def test_municipality_index(self):
        response = self.view.index()

        locations = response['locations']
        self.assertEquals(locations, Municipality.all())
        self.assertNotEquals(len(locations), 0)

    def test_municipality_show(self):
        municipality = Municipality.get(Municipality.name == "Brasillia")
        self.request.context = municipality

        response = self.view.show()

        self.assertEqual(response['parent'], municipality)
        self.assertEqual(response['locations'], municipality.clinics)
        self.assertNotEqual(len(response['locations']), 0)
