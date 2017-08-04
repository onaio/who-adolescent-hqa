from collections import Counter
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer)
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
INITIAL_SCORE_MAP = {characteristics.EQUITABLE: 0,
                     characteristics.ACCESSIBLE: 0,
                     characteristics.ACCEPTABLE: 0,
                     characteristics.APPROPRIATE: 0,
                     characteristics.EFFECTIVE: 0}


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
    period = relationship(
        'ReportingPeriod',
        backref=backref('reports',
                        cascade="all, delete, delete-orphan"))

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
        clinic_count = len(clinics)

        results = reduce(lambda x, y: Counter(x) + Counter(y),
                         (c.key_indicators(period) for c in clinics),
                         INITIAL_SCORE_MAP)

        if clinic_count > 0:
            reports = {
                key: (value / clinic_count)
                for key, value in results.items()
                if value is not 0}
        else:
            reports = INITIAL_SCORE_MAP

        return reports
