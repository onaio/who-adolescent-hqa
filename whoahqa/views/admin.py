from deform import Form, ValidationFailure, Button
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound

from whoahqa.constants import permissions as perms
from whoahqa.forms import UserForm
from whoahqa.models import (
    OnaUser,
    UserFactory)


@view_defaults(route_name='admin',
               context=OnaUser,
               permission=perms.SUPER_USER)
class AdminViews(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='',
                 context=UserFactory,
                 renderer='admin_users_list.jinja2')
    def list(self):
        users = OnaUser.all()
        return {
            'users': users
        }

    @view_config(name='edit', renderer='admin_users_edit.jinja2')
    def edit(self):
        user = self.request.context
        form = Form(
            UserForm().bind(
                request=self.request,
                user=user),
            buttons=('Save', Button(name='cancel', type='button')),
            appstruct=user.appstruct)
        if self.request.method == 'POST':
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                pass
            else:
                user.update(
                    values['group'],
                    values['municipality_id'],
                    values['active'])
                self.request.session.flash(
                    "Your changes have been saved", 'success')
                return HTTPFound(
                    self.request.route_url(
                        'users', traverse=(user.id, 'edit')))
        return {
            'form': form
        }
