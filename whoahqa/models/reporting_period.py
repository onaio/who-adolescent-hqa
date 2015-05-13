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

DATE_FORMAT = "%d-%m-%Y"


def get_current_date():
    return datetime.datetime.now()


class ReportingPeriod(Base):
    __tablename__ = 'reporting_periods'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    start_date = Column(Date(), nullable=False)
    end_date = Column(Date(), nullable=False)
    form_xpath = Column(String(100), nullable=True)

    @classmethod
    def get_active_periods(cls):
        # today = get_current_date()

        # return DBSession.query(ReportingPeriod).filter(
        #     ReportingPeriod.start_date <= today).order_by(
        #     "start_date desc").all()

        return DBSession.query(ReportingPeriod).order_by(
            "start_date asc").all()

    @classmethod
    def get_current_period(cls):
        today = get_current_date()
        return DBSession.query(ReportingPeriod).filter(
            ReportingPeriod.start_date <= today).order_by(
            "start_date desc").limit(1).one()

    @property
    def appstruct(self):
        return {
            'title': self.title,
            'form_xpath': self.form_xpath,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'id': self.id
        }

    def update(self, **kwargs):
        self.title = kwargs['title']
        self.form_xpath = kwargs['form_xpath']
        self.start_date = kwargs['start_date']
        self.end_date = kwargs['end_date']

        self.save()


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
