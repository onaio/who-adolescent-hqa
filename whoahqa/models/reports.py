from sqlalchemy import (
    Column,
    ForeignKey,
    func,
    Integer,
    Numeric)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import (
    backref,
    relationship)
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound)

from whoahqa.constants import characteristics
from whoahqa.models import (
    Base,
    DBSession)

AVERAGE_SCORE_KEY = 'average_score'


class ClinicReport(Base):
    __tablename__ = 'clinic_reports'
    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    clinic = relationship('Clinic',
                          backref=backref(
                              'reports',
                              cascade="all, delete, delete-orphan"),
                          single_parent=True)

    period_id = Column(Integer, ForeignKey('reporting_periods.id'))
    period = relationship('ReportingPeriod')

    json_data = Column(JSON, nullable=False)

    def generate_report_data(self):
        self.json_data = self.clinic.get_key_indicator_scores(
            self.period.form_xpath)

    def update(self):
        self.generate_report_data()
        self.save()

    def get_key_indicators(self):
        return self.json_data

    @classmethod
    def generate_clinic_report(cls, clinic, period):
        # Generate report and save it
        report = ClinicReport(clinic=clinic, period=period)
        # Pass period argument to get_key_indicator_scores
        key_indicator_scores = clinic.get_key_indicator_scores(
            period.form_xpath)

        if key_indicator_scores:
            report.json_data = key_indicator_scores
            report.save()
            return DBSession.merge(report)

    @classmethod
    def get_or_generate(cls, clinic, period):
        """
        If report does not exist for requested reporting period,
        generate and cache it.
        """
        try:
            report = ClinicReport.get(ClinicReport.clinic == clinic,
                                      ClinicReport.period == period)
        except NoResultFound:
            report = cls.generate_clinic_report(clinic, period)
        except MultipleResultsFound:
            reports = ClinicReport.all(ClinicReport.clinic == clinic,
                                       ClinicReport.period == period)
            report = reports[-1]

        return report

    @classmethod
    def get_clinic_reports(cls, clinics, period):
        reports = None
        clinic_ids = [c.id for c in clinics]
        clinic_count = len(clinics)

        results = DBSession.query(
            func.sum(
                ClinicReport.json_data['equitable'].astext.cast(Numeric)),
            func.sum(
                ClinicReport.json_data['accessible'].astext.cast(Numeric)),
            func.sum(
                ClinicReport.json_data['acceptable'].astext.cast(Numeric)),
            func.sum(
                ClinicReport.json_data['appropriate'].astext.cast(Numeric)),
            func.sum(ClinicReport.json_data['effective'].astext.cast(Numeric))
        ).filter(ClinicReport.clinic_id.in_(clinic_ids))\
         .filter(ClinicReport.period == period).first()

        report_data = {characteristics.EQUITABLE: results[0] or 0,
                       characteristics.ACCESSIBLE: results[1] or 0,
                       characteristics.ACCEPTABLE: results[2] or 0,
                       characteristics.APPROPRIATE: results[3] or 0,
                       characteristics.EFFECTIVE: results[4] or 0}

        if clinic_count > 0:
            reports = {
                key: (value / clinic_count)
                for key, value in report_data.items()}
        else:
            reports = report_data

        return reports
