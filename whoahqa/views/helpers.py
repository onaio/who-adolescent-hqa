from sqlalchemy.orm.exc import NoResultFound
from whoahqa.models import ReportingPeriod


def get_period_from_request(request):
    try:
        period = ReportingPeriod.get(
            ReportingPeriod.id == request.GET.get('period', 0))
    except NoResultFound:
        period = ReportingPeriod.get_current_period()

    return period
