from pyramid import testing
from whoahqa.tests import IntegrationTestBase
from whoahqa.models import State, Municipality, Clinic
from whoahqa.views.push_data import push_facilities


class TestPushData(IntegrationTestBase):

    def setUp(self):
        super(TestPushData, self).setUp()
        self.request = testing.DummyRequest()

    def test_push_facilities_with_empty_locations(self):
        response = push_facilities(self.request)

        self.assertListEqual(
            response['header'],
            ['CNES', 'state', 'municipality', 'facility_name'])

        self.assertEqual(len(response['rows']), 0)

    def test_push_facilities_with_locations(self):
        # create dummy data
        self._create_state()
        self._create_municipality()

        municipality = Municipality.newest()
        state = State.newest()
        municipality.parent = state
        municipality.save()

        clinic1 = Clinic(id=1,
                         name=u"Clinic A",
                         code="1A2B",
                         municipality=municipality)
        clinic1.save()

        # test push_facilities service
        response = push_facilities(self.request)

        self.assertEqual(len(response['rows']), 1)
