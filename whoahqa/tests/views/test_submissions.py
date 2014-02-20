from pyramid import testing
from whoahqa.models import (
    DBSession,
    Clinic,
)
from whoahqa.views import (
    SubmissionViews,
)
from whoahqa.tests import (IntegrationTestBase, FunctionalTestBase,)


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

        #should return a 202 response code
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.body,
                         'Accepted pending manual matching process')

    def test_json_post_without_clinic_id(self):
        response = self.post_json('{"test":"1234"}')

        #should return a 202 response code
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.body,
                         'Accepted pending manual matching process')


class TestSubmissionViewsFunctional(FunctionalTestBase):
    def test_json_post_allows_authenticated(self):
        self.setup_test_data()
        url = self.request.route_path('submissions', traverse=())
        payload = self.submissions[2]
        headers = self._login_user('manager_b')
        response = self.testapp.post(url, payload, headers=headers)
        self.assertEqual(response.status_code, 201)