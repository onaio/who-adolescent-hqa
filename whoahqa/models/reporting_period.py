import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date
)
from whoahqa.models import (
    Base,
    BaseModelFactory,
    DBSession)
from sqlalchemy.orm.exc import NoResultFound


def get_current_date():
    return datetime.datetime.now()


class ReportingPeriod(Base):
    __tablename__ = 'reporting_periods'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    start_date = Column(Date(), nullable=False)
    end_date = Column(Date(), nullable=False)

    def generate_form_key(self):
        """ Generates the key used to filter out submissions belonging to this
        reporting period for a clinic.
        """
        if self.end_date.year - self.start_date.year >= 1:
            period = "{}_{}".format(self.start_date.strftime("%-d%b_%Y"),
                                    self.end_date.strftime("%-d%b_%Y"))
        else:
            period = "{}_{}".format(self.start_date.strftime("%-d%b"),
                                    self.end_date.strftime("%-d%b_%Y"))

        return period.lower()

    @classmethod
    def get_active_periods(self):
        # today = get_current_date()

        # return DBSession.query(ReportingPeriod).filter(
        #     ReportingPeriod.start_date <= today).order_by(
        #     "start_date desc").all()

        return DBSession.query(ReportingPeriod).order_by(
            "start_date asc").all()

    @classmethod
    def get_current_period(self):
        today = get_current_date()
        return DBSession.query(ReportingPeriod).filter(
            ReportingPeriod.start_date <= today).order_by(
            "start_date desc").limit(1).one()


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
