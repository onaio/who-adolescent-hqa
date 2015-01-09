import colander

from deform.widget import SelectWidget

from whoahqa.constants.groups import GROUPS


def key_to_label(key):
    return key.capitalize().replace("_", " ")


@colander.deferred
def user_role_widget(node, kw):
    return SelectWidget(
        values=[(g, key_to_label(g)) for g in GROUPS])


class UserForm(colander.MappingSchema):
    group = colander.SchemaNode(
        colander.String(encoding='utf-8'), title="Role",
        widget=user_role_widget)

    def validator(self, node, value):
        exc = colander.Invalid(node, "")
        valid = True
        if value['group'] not in GROUPS:
            valid = False
        if not valid:
            raise exc
