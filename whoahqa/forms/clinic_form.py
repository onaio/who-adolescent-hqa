import colander

from deform.widget import SelectWidget

from whoahqa.models import Municipality
from whoahqa.utils import translation_string_factory as _
from ..utils import format_location_name as fmt


@colander.deferred
def municipality_widget(node, kw):
    values = [('', '---')]
    [values.append((m.id, fmt(m.name))) for m in Municipality.all()]
    return SelectWidget(
        values=values)


class ClinicForm(colander.MappingSchema):
    name = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title=_(u"Clinic Name"))
    code = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title=_(u"CNES Number"))
    municipality = colander.SchemaNode(
        colander.String(encoding='utf-8'), title=_(u"Municipality"),
        widget=municipality_widget)

    def validator(self, node, value):
        exc = colander.Invalid(node, "")
        valid = True
        if not value['name'] or not value['code']:
            valid = False

        if not valid:
            raise exc
