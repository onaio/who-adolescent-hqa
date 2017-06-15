from deform import Form, ValidationFailure, Button
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound

from whoahqa.constants import permissions as perms
from whoahqa.forms import UserForm
from whoahqa.models import (
    OnaUser,
    User,
    UserFactory)
from whoahqa.views.helpers import get_period_from_request
from whoahqa.utils import translation_string_factory as _


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
        users = OnaUser.all()
        period = get_period_from_request(self.request)

        return {
            'users': users,
            'period': period
        }

    @view_config(name='edit',
                 renderer='admin_users_edit.jinja2')
    def edit(self):
        user = self.request.context
        ona_user = user.ona_user
        form = Form(
            UserForm().bind(
                request=self.request,
                user=ona_user),
            buttons=('Save', Button(name='cancel', type='button')),
            appstruct=user.appstruct)
        if self.request.method == 'POST':
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                pass
            else:
                ona_user.update(values)
                self.request.session.flash(
                    _("Your changes have been saved"), 'success')
                return HTTPFound(
                    self.request.route_url(
                        'admin', traverse=(user.id, 'edit')))

        period = get_period_from_request(self.request)

        return {
            'form': form,
            'ona_user': ona_user,
            'period': period
        }
