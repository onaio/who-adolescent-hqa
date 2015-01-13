from sqlalchemy import (
    Column,
    Integer,
    String,
    Date
)
from whoahqa.models import Base, BaseModelFactory
from sqlalchemy.orm.exc import NoResultFound


class ReportingPeriod(Base):
    __tablename__ = 'reporting_periods'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    start_date = Column(Date(), nullable=False)
    end_date = Column(Date(), nullable=False)


class ReportingPeriodFactory(BaseModelFactory):

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
