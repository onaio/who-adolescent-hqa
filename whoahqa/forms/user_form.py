import colander

from deform.widget import (
    SelectWidget,
    CheckedPasswordWidget)

from whoahqa.constants.groups import GROUPS
from whoahqa.models import (
    Clinic,
    Municipality,
    State)


def key_to_label(key):
    return key.capitalize().replace("_", " ")


@colander.deferred
def user_role_widget(node, kw):
    return SelectWidget(
        values=[(g, key_to_label(g)) for g in GROUPS])


@colander.deferred
def municipality_selection_widget(node, kw):
    return SelectWidget(
        values=[(m.id, key_to_label(m.name)) for m in Municipality.all()])


@colander.deferred
def state_selection_widget(node, kw):
    return SelectWidget(
        values=[(m.id, key_to_label(m.name)) for m in State.all()])


@colander.deferred
def clinic_selection_widget(node, kw):
    return SelectWidget(
        values=[(c.id, key_to_label(c.name + " - " + c.code))
                for c in Clinic.all()],
        multiple=True)


class UserForm(colander.MappingSchema):
    group = colander.SchemaNode(
        colander.String(encoding='utf-8'), title="Role",
        widget=user_role_widget)

    clinics = colander.SchemaNode(
        colander.Set(), title="Clinic",
        missing='',
        widget=clinic_selection_widget)

    municipality = colander.SchemaNode(
        colander.String(encoding='utf-8'), title="Municipality",
        missing='',
        widget=municipality_selection_widget)

    state = colander.SchemaNode(
        colander.String(encoding='utf-8'), title="State",
        missing='',
        widget=state_selection_widget)

    password = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        validator=colander.Length(min=5),
        widget=CheckedPasswordWidget(),
        missing='',
        title="Change Password")

    def validator(self, node, value):
        exc = colander.Invalid(node, "")
        valid = True
        if value['group'] not in GROUPS:
            valid = False
        if not valid:
            raise exc
