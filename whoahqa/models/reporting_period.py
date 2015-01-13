from pyramid.security import (
    Allow,
    ALL_PERMISSIONS)

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date
)
from whoahqa.constants import groups, permissions as perms
from whoahqa.models import Base, BaseModelFactory
from sqlalchemy.orm.exc import NoResultFound


class ReportingPeriod(Base):
    __tablename__ = 'reporting_periods'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    start_date = Column(Date(), nullable=False)
    end_date = Column(Date(), nullable=False)


class ReportingPeriodFactory(BaseModelFactory):
    __acl__ = [
        (Allow, groups.SUPER_USER, ALL_PERMISSIONS),
        (Allow, groups.MUNICIPALITY_MANAGER, perms.CAN_CREATE_PERIOD),
        (Allow, groups.CLINIC_MANAGER, perms.CAN_LIST_CLINICS)
    ]

    def __getitem__(self, item):
        try:
            period_id = int(item)
            period = ReportingPeriod.get(ReportingPeriod.id == period_id)
        except (ValueError, NoResultFound):
            raise KeyError
        else:
            period.__parent__ = self
            period.__name__ = item
            return period
