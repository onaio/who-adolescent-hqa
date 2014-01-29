from sqlalchemy import (
    Column,
    Index,
    ForeignKey,
    Integer,
    String,
    Text,
    Table
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    synonym
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class RootFactory(object):
    def __init__(self, request):
        pass


class ClinicFactory(object):
    def __init__(self, request):
        self.request = request

    def __getitem__(self, item):
        pass

    @classmethod
    def get_unassigned_clinics(cls):
        clinics = DBSession.query(Clinic).outerjoin(user_clinics).filter(
            "user_clinics.clinic_id IS NULL").all()
        return clinics


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


class Clinic(Base):
    __tablename__ = 'clinics'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
