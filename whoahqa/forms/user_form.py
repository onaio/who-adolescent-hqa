import colander

from deform.widget import (
    SelectWidget,
    TextInputWidget,
    CheckedPasswordWidget)

from whoahqa.utils import translation_string_factory as _

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
    values = [('', '---')]
    [values.append((m.id, key_to_label(m.name))) for m in Municipality.all()]

    return SelectWidget(values=values)


@colander.deferred
def state_selection_widget(node, kw):
    values = [('', '---')]
    [values.append((m.id, key_to_label(m.name))) for m in State.all()]

    return SelectWidget(values=values)


@colander.deferred
def clinic_selection_widget(node, kw):
    values = [('', '---')]
    [values.append((c.id, key_to_label(c.name + " - " + c.code)))
     for c in Clinic.all()]
    return SelectWidget(
        values=values,
        multiple=True)


class UserForm(colander.MappingSchema):
    email = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        widget=TextInputWidget(),
        missing='',
        title=_(u"Email Address"))
    group = colander.SchemaNode(
        colander.String(encoding='utf-8'), title=_(u"Role"),
        widget=user_role_widget)

    clinics = colander.SchemaNode(
        colander.Set(), title=_(u"Clinic"),
        missing='',
        widget=clinic_selection_widget)

    municipality = colander.SchemaNode(
        colander.String(encoding='utf-8'), title=_(u"Municipality"),
        missing='',
        widget=municipality_selection_widget)

    state = colander.SchemaNode(
        colander.String(encoding='utf-8'), title=_(u"State"),
        missing='',
        widget=state_selection_widget)

    password = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        validator=colander.Length(min=5),
        widget=CheckedPasswordWidget(),
        missing='',
        title=_(u"Change Password"))

    def validator(self, node, value):
        exc = colander.Invalid(node, "")
        valid = True
        if value['group'] not in GROUPS:
            valid = False
        if not valid:
            raise exc
