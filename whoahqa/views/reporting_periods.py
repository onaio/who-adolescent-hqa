import urlparse

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config, view_defaults
from deform import Form, ValidationFailure

from whoahqa.constants import permissions as perms
from whoahqa.utils import translation_string_factory as _
from whoahqa.utils import valid_year
from whoahqa.models import DBSession, ReportingPeriod
from whoahqa.forms import ReportingPeriodForm
from whoahqa.views.base import BaseClassViews


@view_defaults(route_name='periods')
class ReportingPeriodViews(BaseClassViews):

    @view_config(
        name='list',
        permission=perms.CAN_LIST_CLINICS,
        renderer='reporting_periods_list.jinja2')
    def list(self):
        # This lists all periods including those in the future
        periods = ReportingPeriod.all()
        return {
            'periods': periods,
            'period': ReportingPeriod.get_current_period()}

    @view_config(
        name='new',
        permission=perms.CAN_CREATE_PERIOD,
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
            except ValidationFailure:
                self.request.session.flash(
                    _(u"Please fix the errors indicated below."), 'error')
            else:
                available_xpaths = [1, 2, 3, 4, 5]
                if payload['form_xpath'] not in available_xpaths and \
                   valid_year(payload['form_xpath']) is None:
                    self.request.session.flash(
                        _(u"Only numeric values 1-5 and calendar "
                          "years (YYYY) allowed."), 'error')
                else:
                    period = ReportingPeriod(
                        title=payload['title'],
                        form_xpath=payload['form_xpath'],
                        start_date=payload['start_date'],
                        end_date=payload['end_date'])
                    DBSession.add(period)
                    DBSession.flush()
                    self.request.session.flash(
                        _(u"Reporting period created"),
                        'success')
                    return HTTPFound(
                        self.request.route_url('periods', traverse=('list')))

        # render form
        return {
            'form': form,
            'period': ReportingPeriod.get_current_period()}

    @view_config(
        name='edit',
        permission=perms.CAN_CREATE_PERIOD,
        renderer='reporting_periods_create.jinja2',
        context=ReportingPeriod)
    def edit(self):
        period = self.request.context
        form = Form(
            ReportingPeriodForm().bind(
                request=self.request,
                period=period),
            buttons=('Save',),
            css_class='form-horizontal',
            appstruct=period.appstruct)
        if self.request.method == "POST":
            post = self.request.POST.items()
            try:
                payload = form.validate(post)
            except ValidationFailure:
                self.request.session.flash(
                    _(u"Please fix the errors indicated below."), 'error')
            else:
                available_xpaths = [1, 2, 3, 4, 5]
                if payload['form_xpath'] not in available_xpaths and \
                   valid_year(payload['form_xpath']) is None:
                    self.request.session.flash(
                        _(u"Only numeric values 1-5 and calendar "
                          "years (YYYY) allowed."), 'error')
                else:
                    period.update(**payload)

                    self.request.session.flash(
                        _(u"Your changes have been saved"),
                        'success')
                    return HTTPFound(
                        self.request.route_url('periods', traverse=('list')))

        # render form
        return {
            'form': form,
            'period': period
        }

    @view_config(name='redirect',
                 context=ReportingPeriod)
    def redirect(self):
        period = self.request.context
        came_from = self.request.GET.get('came_from')
        target_url = urlparse.unquote(came_from).format(period_id=period.id)
        return HTTPFound(target_url)
