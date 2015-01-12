import colander

from deform.widget import SelectWidget

from whoahqa.models import Municipality
from whoahqa.utils import translation_string_factory as _


@colander.deferred
def municipality_widget(node, kw):
    return SelectWidget(
        values=[(m.id, m.name) for m in Municipality.all()])


class ClinicForm(colander.MappingSchema):
    name = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title=_("Clinic Name"))
    code = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title=_("Clinic Code"))
    municipality = colander.SchemaNode(
        colander.String(encoding='utf-8'), title="Municipality",
        widget=municipality_widget)

    def validator(self, node, value):
        exc = colander.Invalid(node, "")
        valid = True
        if not value['name'] or not value['code']:
            valid = False

        if not valid:
            raise exc
