import transaction
import json

from sqlalchemy import (
    Column,
    Index,
    ForeignKey,
    Integer,
    String,
    Text,
    Table
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import desc

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    synonym
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
CLINIC_IDENTIFIER = 'clinic_id'
CHARACTERISTIC = 'characteristic'
XFORM_ID = 'xform_id'


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


# TODO: Add a UNIQUE key constraint on both clinic_id and submission_id
# together
clinic_submissions = Table(
    'clinic_submissions',
    Base.metadata,
    Column('clinic_id', Integer, ForeignKey('clinics.id')),
    Column('submission_id', Integer, ForeignKey('submissions.id'))
)


class Clinic(Base):
    __tablename__ = 'clinics'
    id = Column(Integer, primary_key=True)
    # TODO: Add unique constraint on identifier
    identifier = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    user = relationship("User", secondary=user_clinics, uselist=False)
    submissions = relationship("Submission", secondary=clinic_submissions)

    def assign_to(self, user):
        self.user = user
        DBSession.add(self)

    @classmethod
    def get_unassigned(cls):
        clinics = DBSession.query(Clinic).outerjoin(user_clinics).filter(
            user_clinics.columns.clinic_id == None).all()
        return clinics


class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True)
    raw_data = Column(JSON, nullable=False)

    @classmethod
    def save(cls, payload):
        submission = Submission(raw_data=payload)
        DBSession.add(submission)

        parsed_json = cls.parse_json(payload)
        # check if we have a valid clinic with said id
        clinic_identifier = parsed_json.get(CLINIC_IDENTIFIER)
        if clinic_identifier:
            try:
                clinic = Clinic.get(Clinic.identifier == clinic_identifier)
            except NoResultFound:
                pass
            else:
                clinic.submissions.append(submission)
                DBSession.add(clinic)

    @classmethod
    def parse_json(cls, json_string):
        json_data = json.loads(json_string)
        return {
            CLINIC_IDENTIFIER: json_data.get('clinic_id'),
            CHARACTERISTIC: json_data.get('facility_info/HS_char'),
            XFORM_ID: json_data.get('_xform_id_string'),
        }

