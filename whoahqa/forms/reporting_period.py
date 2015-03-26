import datetime

import colander
from deform.widget import TextInputWidget

from whoahqa.utils import translation_string_factory as _


DATE_FORMAT = "%d-%m-%Y"


class MonthYearDate(object):
    """ Custom type that converts between MM-YYYY strings and their date
    representation.
    """
    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null

        if not isinstance(appstruct, datetime.datetime):
            raise colander.Invalid(
                node, _(u"{} is not a valid date".format(appstruct)))

        return appstruct.strftime(DATE_FORMAT)

    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.null

        if not isinstance(cstruct, basestring):
            raise colander.Invalid(node, '%r is not a string' % cstruct)

        try:
            value = datetime.datetime.strptime(cstruct, DATE_FORMAT)
        except Exception:
            raise colander.Invalid(
                node,
                "date string {} does not match the format 'MM-YYYY'".format(
                    cstruct))
        else:
            return value

    def cstruct_children(self, node, cstruct):
        return []


class StartEndDateValidator(object):
    def __call__(self, node, value):
        if value['start_date'] >= value['end_date']:
            raise colander.Invalid(
                node['start_date'],
                _(u"Start date must be earlier than end date"))


class ReportingPeriodForm(colander.MappingSchema):
    validator = StartEndDateValidator()
    title = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title=_(u"Name"),
        description=_(u"Give the reporting period a name",))
    start_date = colander.SchemaNode(
        MonthYearDate(),
        title=_(u"Start Date"),
        widget=TextInputWidget(),
        missing_msg=_(u"Start date is required"))
    end_date = colander.SchemaNode(
        MonthYearDate(),
        title=_(u"End Date"),
        widget=TextInputWidget(),
        missing_msg=_(u"End date is required"))
