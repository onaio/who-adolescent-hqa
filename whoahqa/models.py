import json

from pyramid.security import (
    Allow,
    Authenticated,
    ALL_PERMISSIONS,
)

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

from whoahqa import constants

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


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
    __acl__ = [
        (Allow, 'g:su', ALL_PERMISSIONS)
    ]

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
    __acl__ = [
        (Allow, 'g:su', ALL_PERMISSIONS)
    ]

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


user_groups = Table(
    'user_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    clinics = relationship("Clinic", secondary=user_clinics)
    groups = relationship("Group", secondary=user_groups)

    def get_clinics(self):
        clinics = DBSession.query(Clinic).join(user_clinics).filter(
            user_clinics.columns.user_id == self.id).all()
        return clinics

    @property
    def __acl__(self):
        return [
            (Allow, "u:{}".format(self.id), ALL_PERMISSIONS),
        ]


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)


class OnaUser(Base):
    __tablename__ = 'ona_users'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True,
                     autoincrement=False)
    username = Column(String(255), nullable=False, unique=True)
    refresh_token = Column(String(255), nullable=False)
    user = relationship('User')

    @classmethod
    def get_or_create_from_api_data(cls, json_data, refresh_token):
        # check that data has length of 1 and raise ValueError otherwise
        if len(json_data) != 1:
            raise ValueError("We only know how to handle a single user")

        data = json_data[0]
        username = data['username']
        try:
            ona_user = OnaUser.get(OnaUser.username == username)
            ona_user.refresh_token = refresh_token
        except NoResultFound:
            user = User()
            ona_user = OnaUser(username=username, refresh_token=refresh_token)
            ona_user.user = user
        DBSession.add(ona_user)
        return ona_user


class ClinicSubmission(Base):
    __tablename__ = 'clinic_submissions'
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    submission_id = Column(
        Integer, ForeignKey('submissions.id'), primary_key=True)
    characteristic = Column(String, nullable=False, primary_key=True)
    xform_id = Column(String, nullable=False, primary_key=True)
    submission = relationship("Submission")


class Clinic(Base):
    __tablename__ = 'clinics'
    id = Column(Integer, primary_key=True)
    code = Column(String(100), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    user = relationship("User", secondary=user_clinics, uselist=False)

    def assign_to(self, user):
        self.user = user
        DBSession.add(self)

    @property
    def is_assigned(self):
        return self.user is not None

    @classmethod
    def get_unassigned(cls):
        clinics = DBSession.query(Clinic).outerjoin(user_clinics).filter(
            user_clinics.columns.clinic_id == None).all()
        return clinics

    def calculate_score(self, characteristic, xform_id):
        """
        Calculate the aggregate score and the no. of respondents for the
        characteristic/xform_id pair
        """
        # get the questions in this client tool for this characteristic
        question_xpaths = constants.\
            CHARACTERISTIC_MAPPING[characteristic][xform_id]

        submissions_table = Base.metadata.tables['submissions']
        clinic_submissions_table = Base.metadata.tables['clinic_submissions']

        # for each question, select from clinic_submissions where the
        # clinic_id matches self's and characteristic and the client tool are
        # also a match to the requested ones. Joint to submissions to do an
        # aggregation
        aggregate_score = .0
        num_responses = DBSession.execute(
            select(['COUNT(*)'])
            .select_from(clinic_submissions_table)
            .where(
                and_(
                    clinic_submissions_table.c.clinic_id == self.id,
                    clinic_submissions_table.c.characteristic ==
                    characteristic,
                    clinic_submissions_table.c.xform_id == xform_id
                )
            )).scalar()
        # convert to float once
        denominator = float(num_responses)

        # simple optimization, if num_responses is zero i.e. no responses return
        # now
        if num_responses == 0:
            return None, 0

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
            aggregate_score += float(numerator)/denominator

        return aggregate_score, num_responses

    def get_scores(self):
        """
        scores = {
            'one': {
                'adolescent_quality_assementEnSp': {
                    'aggregate_score': 1.5,
                    'num_questions': 2,
                    'num_responses': 4,
                    'num_expected_responses': 5
                },
                'totals': {
                    'total_scores': 3
                    'total_questions': 5,
                }
            }
        }
        """
        scores = {}

        for characteristic, label in constants.CHARACTERISTICS:
            scores[characteristic] = {}
            total_scores = total_questions = total_responses = 0
            mapping = constants.CHARACTERISTIC_MAPPING[characteristic]
            for client_tool_id, questions in mapping.items():
                aggregate_score, num_responses = self.calculate_score(
                    characteristic, client_tool_id)
                stats = {
                    'aggregate_score': aggregate_score,
                    'num_responses': num_responses,
                    'num_questions': len(questions),
                }
                scores[characteristic][client_tool_id] = stats

                # increment total if value is not None
                if aggregate_score is not None:
                    total_scores += aggregate_score

                total_questions += len(questions)
                total_responses += num_responses

            scores[characteristic]['totals'] = {
                'total_scores': None if total_scores == 0 else total_scores,
                'total_questions': total_questions,
                'total_responses': total_responses,
                'total_percentage': None if total_responses == 0 else (
                    total_scores/float(total_questions) * 100)
            }

        return scores


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
        characteristics = json_data.get(
            constants.CHARACTERISTIC, '').split(" ")
        return (json_data.get('facility_info/clinic_id'),
                characteristics,
                json_data.get('_xform_id_string'),)

