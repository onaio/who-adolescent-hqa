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

    def generate_form_key(self):
        # generate reporting period based on the new convention
        """
        1may_31jul_2015 <=> 1 May - 31 Jul 2015
        1aug_31oct_2015 <=> 1 Aug - 31 Oct 2015
        1nov_2015_31jan_2016  <=>  1 Nov 2015 - 31 Jan 2016
        1feb_30apr_2016 <=> 1 Feb - 30 Apr 2016
        format string = ("%d%b%Y")
        """
        if self.end_date.year - self.start_date.year >= 1:
            period = "{}_{}".format(self.start_date.strftime("%-d%b_%Y"),
                                    self.end_date.strftime("%-d%b_%Y"))
        else:
            period = "{}_{}".format(self.start_date.strftime("%-d%b"),
                                    self.end_date.strftime("%-d%b_%Y"))

        return period.lower()


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
