import json

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Table
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql import select, and_

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

CLINIC_IDENTIFIER = 'facility_info/clinic_id'
CHARACTERISTIC = 'facility_info/HS_char'
XFORM_ID = '_xform_id_string'


class BaseModel(object):
    @classmethod
    def newest(cls):
        return DBSession.query(cls).order_by(desc(cls.id)).first()

    @classmethod
    def get(cls, *criterion):
        return DBSession.query(cls).filter(*criterion).one()

    @classmethod
    def all(cls, *criterion):
        return DBSession.query(cls).filter(*criterion).all()

    @classmethod
    def count(cls, *criterion):
        return DBSession.query(cls).filter(*criterion).count()

Base = declarative_base(cls=BaseModel)


class RootFactory(object):
    def __init__(self, request):
        self.request = request


class UserFactory(object):
    def __init__(self, request):
        self.request = request

    def __getitem__(self, item):
        # try to retrieve the user whose id matches item
        try:
            user = DBSession.query(User).filter_by(id=item).one()
        except NoResultFound:
            raise KeyError
        else:
            user.__parent__ = self
            user.__name__ = item
            return user


class ClinicFactory(object):
    def __init__(self, request):
        self.request = request

    def __getitem__(self, item):
        # try to retrieve the clinic whose id matches item
        try:
            clinic_id = int(item)
            clinic = DBSession.query(Clinic).filter_by(id=clinic_id).one()
        except (ValueError, NoResultFound):
            raise KeyError
        else:
            clinic.__parent__ = self
            clinic.__name__ = item
            return clinic


class SubmissionFactory(object):
    def __init__(self, request):
        self.request = request

    def __getitem__(self, item):
        raise NotImplementedError


user_clinics = Table(
    'user_clinics',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('clinic_id', Integer, ForeignKey('clinics.id'))
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    clinics = relationship("Clinic", secondary=user_clinics)

    def get_clinics(self):
        clinics = DBSession.query(Clinic).join(user_clinics).filter(
            user_clinics.columns.user_id == self.id).all()
        return clinics


class ClinicSubmission(Base):
    __tablename__ = 'clinic_submissions'
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    submission_id = Column(
        Integer, ForeignKey('submissions.id'), primary_key=True)
    characteristic = Column(String, nullable=False, primary_key=True)
    xform_id = Column(String, nullable=False, primary_key=True)
    submission = relationship("Submission")


# Client Tool Constants
ADOLESCENT_CLIENT = 'adolescent_quality_assementEnSp'
HEALTH_CARE_PROVIDER = 'health_care_provider_interview_EnSp'
SUPPORT_STAFF = 'support_staff_interview_EnSp'
HEALTH_FACILITY_MANAGER = 'health_facility_manager_interview_EnSp'
OUTREACH_WORKER = 'outreach_worker_interview_EnSp'
COMMUNITY_MEMBER = 'community_member_interview_EnSp'
ADOLESCENT_IN_COMMUNITY = 'adolescent_in_community_tool_EnSp'
OBSERVATION_GUIDE = 'observation_guide_EnSp'

CLIENT_TOOLS = [
    (ADOLESCENT_CLIENT, u"AC"),
    (HEALTH_CARE_PROVIDER, u"HC"),
    (SUPPORT_STAFF, u"SS"),
    (HEALTH_FACILITY_MANAGER, u"M"),
    (OUTREACH_WORKER, u"OW"),
    (COMMUNITY_MEMBER, u"CM"),
    (ADOLESCENT_IN_COMMUNITY, u"A in C"),
    (OBSERVATION_GUIDE, u"OG")
]

CHARACTERISTICS = [
    ('one', u"Policies and procedures are in place that do not restrict the "
            u"provision of health services on any terms"),
]

CHARACTERISTIC_MAPPING = {
    'one': {
        ADOLESCENT_CLIENT: (
            'characteristic_one/ch1_q1',
            'characteristic_one/ch1_q2'
        ),
        HEALTH_CARE_PROVIDER: (
            'characteristic_one/ch1_q1',
        ),
        HEALTH_FACILITY_MANAGER: (
            'characteristic_one/ch1_q1',
        ),
        ADOLESCENT_IN_COMMUNITY: (
            'characteristic_one/ch1_q1',
        )
    }
}


class Clinic(Base):
    __tablename__ = 'clinics'
    id = Column(Integer, primary_key=True)
    code = Column(String(100), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    user = relationship("User", secondary=user_clinics, uselist=False)

    def assign_to(self, user):
        self.user = user
        DBSession.add(self)

    @classmethod
    def get_unassigned(cls):
        clinics = DBSession.query(Clinic).outerjoin(user_clinics).filter(
            user_clinics.columns.clinic_id == None).all()
        return clinics

    def calculate_score(self, characteristic, xform_id):
        """
        Calculate a specific characteristic's score for the specified client
        tool
        """
        # get the questions in this client tool for this characteristic
        question_xpaths = CHARACTERISTIC_MAPPING[characteristic][xform_id]

        submissions_table = Base.metadata.tables['submissions']
        clinic_submissions_table = Base.metadata.tables['clinic_submissions']

        # for each question, select from clinic_submissions where the
        # clinic_id matches self's and characteristic and the client tool are
        # also a match to the requested ones. Joint to submissions to do an
        # aggregation
        score = .0
        denominator = float(DBSession.execute(
            select(['COUNT(*)'])
            .select_from(clinic_submissions_table)
            .where(
                and_(
                    clinic_submissions_table.c.clinic_id == self.id,
                    clinic_submissions_table.c.characteristic ==
                    characteristic,
                    clinic_submissions_table.c.xform_id == xform_id
                )
            )).scalar())

        # simple optimization, if denominator is zero i.e. no responses return
        # now
        if denominator == 0:
            return None

        for xpath in question_xpaths:
            numerator = DBSession.execute(
                select(['COUNT(*)'])
                .select_from(clinic_submissions_table.join(
                    submissions_table))
                .where(
                    and_(
                        clinic_submissions_table.c.clinic_id == self.id,
                        clinic_submissions_table.c.characteristic ==
                        characteristic,
                        clinic_submissions_table.c.xform_id == xform_id,
                        submissions_table.c.raw_data[xpath].astext == '1'
                    )
                )).scalar()
            score += float(numerator)/denominator

        return score


class ClinicNotFound(Exception):
    pass


class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True)
    raw_data = Column(JSON, nullable=False)

    @classmethod
    def create_from_json(cls, payload):
        # TODO: check for and handle json.loads parse errors
        submission = Submission(raw_data=json.loads(payload))
        DBSession.add(submission)
        clinic_code, characteristics, xform_id = cls.parse_json(payload)

        # check if we have a valid clinic with said id
        # select([Base.metadata.tables['clinic_submissions'].c.characteristic]).select_from(Base.metadata.tables['clinic_submissions']).join(Base.metadata.tables['submissions'], 'clinic_submissions.submission_id = submissions.id'))
        try:
            clinic = Clinic.get(Clinic.code == clinic_code)
        except NoResultFound:
            raise ClinicNotFound
        else:
            for characteristic in characteristics:
                clinic_submission = ClinicSubmission(
                    clinic_id=clinic.id,
                    submission=submission,
                    characteristic=characteristic,
                    xform_id=xform_id
                )
                DBSession.add(clinic_submission)

    @classmethod
    def parse_json(cls, json_string):
        json_data = json.loads(json_string)
        # split characteristic on [space] for multiple characteristic
        # submissions
        characteristics = json_data.get(CHARACTERISTIC, '').split(" ")
        return (json_data.get('facility_info/clinic_id'),
                characteristics,
                json_data.get('_xform_id_string'),)

