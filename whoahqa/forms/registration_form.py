import colander

from whoahqa.constants.groups import GROUPS

from deform.widget import (
    TextInputWidget,
    CheckedPasswordWidget,
    SelectWidget)

from whoahqa.forms.user_form import (
    clinic_selection_widget,
    municipality_selection_widget,
    state_selection_widget,
    key_to_label)

from whoahqa.utils import translation_string_factory as _

GROUPS.remove('user')


@colander.deferred
def new_user_role_widget(node, kw):
    return SelectWidget(
        values=[(g, key_to_label(g)) for g in GROUPS])


class RegistrationForm(colander.MappingSchema):
    group = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title=_(u"Role"),
        widget=new_user_role_widget)
    clinics = colander.SchemaNode(
        colander.Set(), title=_(u"Clinic"),
        missing='',
        widget=clinic_selection_widget)
    municipality = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title=_(u"Municipality"),
        missing='',
        widget=municipality_selection_widget)
    state = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title=_(u"State"),
        missing='',
        widget=state_selection_widget)
    username = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        validator=colander.Length(
            max=25,
            max_err=_(u'Longer than maximum length 25')),
        widget=TextInputWidget(),
        title=_(u"Username"),
        description=_(u"Type the username of the clinic"))
    password = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        validator=colander.Length(
            min=5,
            min_err=_(u'Shorter than minimum length 5')),
        widget=CheckedPasswordWidget(
            subject=_(u"Password"),
            confirm_subject=_(u"Confirm Password")),
        title=_(u"Password"))

    def validator(self, node, value):
        exc = colander.Invalid(node, "")
        valid = True
        if value['group'] not in GROUPS:
            valid = False

        if not valid:
            raise exc
