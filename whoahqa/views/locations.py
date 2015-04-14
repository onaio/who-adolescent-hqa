from deform import Form, ValidationFailure, Button
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound

from whoahqa.constants import permissions as perms
from whoahqa.views.helpers import get_period_from_request
from whoahqa.forms import LocationForm
from whoahqa.models import (
    DBSession,
    Location,
    LocationFactory)


@view_defaults(route_name='locations',
               permission=perms.SUPER_USER)
class LocationViews(object):
    def __init__(self, request):
        self.request = request
        self.period = get_period_from_request(self.request)

    @view_config(name='',
                 context=LocationFactory,
                 renderer='location_list.jinja2')
    def list(self):
        locations = Location.all()

        return {
            'locations': locations,
            'period': self.period
        }

    @view_config(name='add',
                 context=LocationFactory,
                 renderer='location_form.jinja2')
    def add(self):
        form = Form(
            LocationForm().bind(
                request=self.request),
            buttons=('Save', Button(name='cancel', type='button')))

        if self.request.method == "POST":
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                self.request.session.flash(
                    u"Please fix the errors indicated below.", "error")
            else:
                # add location
                if values['parent_id'] is None:
                    values['parent_id'] = None

                location = Location(**values)
                location.save()

                self.request.session.flash(
                    "{} {} saved".format(
                        location.name, location.location_type),
                    'success')

                # Create new location
                return HTTPFound(
                    self.request.route_url(
                        'locations', traverse=('add')))
        # return form

        return {'form': form,
                'period': self.period}

    @view_config(name='edit',
                 context=Location,
                 renderer='location_form.jinja2')
    def edit(self):
        location = self.request.context

        form = Form(
            LocationForm().bind(
                request=self.request,
                location=location),
            buttons=('Save', Button(name='cancel', type='button')),
            appstruct=location.appstruct)

        if self.request.method == 'POST':
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                pass
            else:
                location.update(**values)

                self.request.session.flash(
                    "Your changes have been saved", 'success')
                return HTTPFound(
                    self.request.route_url(
                        'locations', traverse=(location.id, 'edit')))
        return {
            'form': form,
            'location': location,
            'period': self.period
        }

    @view_config(name='delete',
                 context=Location,
                 request_method='GET')
    def delete(self):
        location = self.request.context
        if not location.children():
            DBSession.delete(location)
        else:
            self.request.session.flash(
                "Cannot delete location with Children", 'error')

        return HTTPFound(
            self.request.route_url('locations', traverse=('')))
