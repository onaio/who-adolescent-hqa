from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPBadRequest,
)
from pyramid.view import (
    view_config,
    view_defaults,
)

from whoahqa.models import (
    SubmissionFactory,
    Submission,
    ClinicNotFound,
)


@view_defaults(route_name='submissions')
class SubmissionViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(
        name='',
        request_method='POST',
        context=SubmissionFactory)
    def json_post(self):
        payload = self.request.body
        if not payload:
            return HTTPBadRequest(comment='Missing JSON Payload')

        try:
            Submission.create_from_json(payload)
        except ClinicNotFound:
            return Response('Accepted Pending Clinic Match', status=202)
        else:
            return Response('Saved', status=201)
