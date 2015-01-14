from sqlalchemy import (
    Column,
    ForeignKey,
    Integer)
from sqlalchemy.dialects.postgresql import JSON

from sqlalchemy.orm import (
    backref,
    relationship)
from sqlalchemy.orm.exc import NoResultFound

from whoahqa.constants import characteristics
from whoahqa.models import (
    Base)

AVERAGE_SCORE_KEY = 'average_score'


class ClinicReport(Base):
    __tablename__ = 'clinic_reports'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    clinic = relationship('Clinics',
                          backref=backref('reports'))

    period_id = Column(Integer, ForeignKey('reporting_periods.id'))
    period = relationship('ReportingPeriod')

    json_data = Column(JSON, nullable=False)

    def get_report(self, clinic, period):
        """
        If report does not exist for requested reporting period,
        generate and cache it.
        """
        try:
            report = ClinicReport.get(ClinicReport.clinic == clinic,
                                      ClinicReport.period == period)
        except NoResultFound:
            # Generate report and save it
            report = ClinicReport(clinic=clinic, period=period)
            report.json_data = clinic.get_all_key_indicator_scores()

            report.save()
        else:
            return report

    def get_key_indicators(self):
        return {
            characteristics.EQUITABLE: self.json_data[
                characteristics.EQUITABLE][AVERAGE_SCORE_KEY],
            characteristics.ACCESSIBLE: self.json_data[
                characteristics.ACCESSIBLE][AVERAGE_SCORE_KEY],
            characteristics.ACCEPTABLE: self.json_data[
                characteristics.ACCEPTABLE][AVERAGE_SCORE_KEY],
            characteristics.APPROPRIATE: self.json_data[
                characteristics.APPROPRIATE][AVERAGE_SCORE_KEY],
            characteristics.EFFECTIVE: self.json_data[
                characteristics.EFFECTIVE][AVERAGE_SCORE_KEY],
        }
