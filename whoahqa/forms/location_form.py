import colander

from deform.widget import SelectWidget

from whoahqa.models import Location
from whoahqa.utils import translation_string_factory as _
from ..utils import format_location_name as fmt


@colander.deferred
def parent_widget(node, kw):
    locations = [('', '---')]
    locations.extend([(l.id, fmt(l.name)) for l in Location.all()])

    return SelectWidget(
        values=locations)


@colander.deferred
def location_type_widget(node, kw):
    location_types = [
        (Location.MUNICIPALITY, Location.MUNICIPALITY.capitalize()),
        (Location.STATE, Location.STATE.capitalize())]

    return SelectWidget(values=location_types)


class LocationForm(colander.MappingSchema):
    name = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title=_(u"Name"))
    location_type = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title=_(u"Location Type"),
        widget=location_type_widget)
    parent_id = colander.SchemaNode(
        colander.String(encoding='utf-8'), title=_(u"Parent Location"),
        widget=parent_widget, missing=None)

    def validator(self, node, value):
        exc = colander.Invalid(node, "")
        valid = True
        if not value['name']:
            valid = False

        if not valid:
            raise exc
