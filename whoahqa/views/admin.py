from deform import Form, ValidationFailure, Button
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.exc import IntegrityError

from whoahqa.constants import permissions as perms
from whoahqa.forms import UserForm, RegistrationForm
from whoahqa.models import (
    User,
    UserFactory,
    DBSession)
from whoahqa.views.helpers import get_period_from_request
from whoahqa.utils import translation_string_factory as _
import transaction


@view_defaults(route_name='admin',
               context=User,
               permission=perms.SUPER_USER)
class AdminViews(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=UserFactory,
                 renderer='admin_users_list.jinja2')
    def list(self):
        users = User.all()
        period = get_period_from_request(self.request)

        return {
            'users': users,
            'period': period
        }

    @view_config(name='edit',
                 renderer='admin_users_edit.jinja2')
    def edit(self):
        user = self.request.context
        dashboard_user = user

        if user.ona_user is not None:
            dashboard_user = dashboard_user.ona_user

        form = Form(
            UserForm().bind(
                request=self.request,
                user=dashboard_user),
            buttons=('Save', Button(name='cancel', type='button')),
            appstruct=user.appstruct)

        if self.request.method == 'POST':
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                pass
            else:
                dashboard_user.update(values)
                self.request.session.flash(
                    _("Your changes have been saved"), 'success')
                return HTTPFound(
                    self.request.route_url(
                        'admin', traverse=(dashboard_user.id, 'edit')))

        period = get_period_from_request(self.request)

        return {
            'form': form,
            'user': dashboard_user,
            'period': period
        }

    @view_config(name='register',
                 context=UserFactory,
                 renderer='register.jinja2')
    def register(self):
        form = Form(
            RegistrationForm().bind(
                request=self.request),
            buttons=('Save',))

        if self.request.method == 'POST':
            data = self.request.POST.items()

            try:
                values = form.validate(data)

            except ValidationFailure:
                self.request.session.flash(
                    _(u"Please fix the highlighted errors below"), "error")

            else:
                try:
                    new_user = User()
                    new_user.update(values)

                    self.request.session.flash(
                        _(u"Success! {} user created".format(
                            new_user.profile.username)),
                        'success')

                    return HTTPFound(
                        self.request.route_url(
                            'admin', traverse=(new_user.id, 'edit')))

                except IntegrityError:
                    transaction.abort()
                    self.request.session.flash(
                        _("Username already in use"), "error")

        return {
            'form': form,
            'period': get_period_from_request(self.request)
        }

    @view_config(name='delete',
                 context=User,
                 renderer='admin_users_list.jinja2')
    def delete(self):
        user = self.request.context

        if self.request.user == user:
            self.request.session.flash(
                _(u"You cannot delete yourself"), "error")
            return HTTPFound(
                self.request.route_url(
                    'admin', traverse=()))

        DBSession.delete(user)

        self.request.session.flash(
            _(u"User successfully deleted"), "success")
        return HTTPFound(
            self.request.route_url(
                'admin', traverse=()))
