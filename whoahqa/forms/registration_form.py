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

GROUPS.remove('user')


@colander.deferred
def new_user_role_widget(node, kw):
    return SelectWidget(
        values=[(g, key_to_label(g)) for g in GROUPS])


class RegistrationForm(colander.MappingSchema):
    email = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        widget=TextInputWidget(),
        missing='',
        title="Email Address")
    group = colander.SchemaNode(
        colander.String(encoding='utf-8'), title="Role",
        widget=new_user_role_widget)
    clinics = colander.SchemaNode(
        colander.Set(), title="Clinic",
        missing='',
        widget=clinic_selection_widget)
    municipality = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title="Municipality",
        missing='',
        widget=municipality_selection_widget)
    state = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title="State",
        missing='',
        widget=state_selection_widget)
    username = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        validator=colander.Length(
            max=25,
            max_err='Longer than maximum length 25'),
        widget=TextInputWidget(),
        title="Username",
        description="Type the username of the clinic")
    password = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        validator=colander.Length(
            min=5,
            min_err='Shorter than minimum length 5'),
        widget=CheckedPasswordWidget(
            subject="Password",
            confirm_subject="Confirm Password"),
        title="Password")

    def validator(self, node, value):
        exc = colander.Invalid(node, "")
        valid = True
        if value['group'] not in GROUPS:
            valid = False

        if not valid:
            raise exc
