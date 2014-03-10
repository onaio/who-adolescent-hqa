import colander
from deform.widget import TextInputWidget

from whoahqa.utils import translation_string_factory as _


class ReportingPeriodForm(colander.MappingSchema):
    # TODO: validate - end_date must be greater than start date
    title = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title=_(u"Name"),
        description=_(u"Give the reporting period a name"))
    start_date = colander.SchemaNode(
        colander.Date(),
        title=_(u"Reporting Period"),
        widget=TextInputWidget())
    end_date = colander.SchemaNode(
        colander.Date(),
        title=_(u"Start Date"),
        widget=TextInputWidget())