from pyramid.security import (
    NO_PERMISSION_REQUIRED,
)
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPBadRequest,
)
from pyramid.view import view_config, view_defaults
from deform import Form, ValidationFailure

from whoahqa.utils import translation_string_factory as _
from whoahqa.models import DBSession, ReportingPeriod
from whoahqa.forms import ReportingPeriodForm
from whoahqa.views.base import BaseClassViews

@view_defaults(route_name='periods')
class ReportingPeriodViews(BaseClassViews):

    @view_config(
        name='',
        permission='list',
        renderer='reporting_periods_list.jinja2')
    def list(self):
        periods = ReportingPeriod.all()
        return {'periods': periods}

    @view_config(
        name='new',
        permission='create',
        renderer='reporting_periods_create.jinja2')
    def create(self):
        form = Form(
            ReportingPeriodForm().bind(),
            buttons=('Save',),
            css_class='form-horizontal')
        if self.request.method == "POST":
            post = self.request.POST.items()
            try:
                payload = form.validate(post)
            except ValidationFailure as e:
                self.request.session.flash(
                    _(u"Please fix the errors indicated below."), 'error')
            else:
                period = ReportingPeriod(
                    title=payload['title'],
                    start_date=payload['start_date'],
                    end_date=payload['end_date'])
                DBSession.add(period)
                DBSession.flush()
                self.request.session.flash(
                    _(u"Reporting period created"),
                    'success')
                return HTTPFound(
                    self.request.route_url('periods', traverse=()))

        # render form
        return {'form': form}
