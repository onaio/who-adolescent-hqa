import colander

from deform.widget import (
    TextInputWidget,
    CheckedPasswordWidget,
    CheckedInputWidget)

from whoahqa.forms.user_form import (
    clinic_selection_widget,
    municipality_selection_widget,
    state_selection_widget,
    user_role_widget)


class RegistrationForm(colander.MappingSchema):
    username = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        validator=colander.Length(max=25),
        widget=TextInputWidget(),
        title="Username",
        description="Type the username of the clinic")
    email = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        widget=CheckedInputWidget(
            subject="Email",
            confirm_subject="Confirm Email"),
        title="Email Address")
    group = colander.SchemaNode(
        colander.String(encoding='utf-8'), title="Role",
        widget=user_role_widget)
    clinics = colander.SchemaNode(
        colander.Set(), title="Clinic",
        widget=clinic_selection_widget)
    municipality = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title="Municipality",
        widget=municipality_selection_widget)
    state = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title="State",
        widget=state_selection_widget)
    password = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        validator=colander.Length(min=5),
        widget=CheckedPasswordWidget(
            subject="Password",
            confirm_subject="Confirm Password"),
        title="Password")

    def validator(self, node, value):
        exc = colander.Invalid(node, "")
        valid = True
        if not value['username']:
            valid = False
        if not valid:
            raise exc
