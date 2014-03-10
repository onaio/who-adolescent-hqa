import json
import random

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
    Table,
    DateTime,
    Date,
    func,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql import select, and_
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    synonym,
)

from zope.sqlalchemy import ZopeTransactionExtension

from whoahqa import constants
from whoahqa.utils import hashid
from whoahqa.constants import permissions as perms
from whoahqa.security import pwd_context

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
random.seed()


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
    __acl__ = [
        (Allow, 'g:su', ALL_PERMISSIONS),
        (Allow, Authenticated, perms.AUTHENTICATED)
    ]

    def __init__(self, request):
        self.request = request


class BaseModelFactory(object):
    def __init__(self, request):
        self.request = request

    @property
    def __parent__(self):
        # set root factory as parent to inherit root's acl
        return RootFactory(self.request)


class UserFactory(BaseModelFactory):
    __acl__ = []

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


class ClinicFactory(BaseModelFactory):
    __acl__ = []

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


class SubmissionFactory(BaseModelFactory):
    __acl__ = []

    def __getitem__(self, item):  # pragma: no cover
        raise NotImplementedError


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


user_clinics = Table(
    'user_clinics',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('clinic_id', Integer, ForeignKey('clinics.id'), nullable=False),
    PrimaryKeyConstraint('user_id', 'clinic_id')
)


user_groups = Table(
    'user_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('group_id', Integer, ForeignKey('groups.id'), nullable=False),
    PrimaryKeyConstraint('user_id', 'group_id')
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


class UserProfile(Base):
    __tablename__ = 'user_profiles'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True,
                     autoincrement=False)
    username = Column(String(100), nullable=False, unique=True)
    pwd = Column(String(255), nullable=False)
    user = relationship('User')

    def check_password(self, password):
        # always return false if password is greater than 255 to avoid
        # spoofing attacks
        if len(password) > 255:
            return False
        return pwd_context.verify(password, self.pwd)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        from .security import pwd_context
        self.pwd = pwd_context.encrypt(value)

    password = synonym('_password', descriptor=password)


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
    date_created = Column(DateTime(timezone=True),
                          server_default=func.now(), nullable=False)
    user = relationship("User", secondary=user_clinics, uselist=False)

    @property
    def __acl__(self):
        acl = []
        if self.user is not None:
            acl.append((Allow, "u:{}".format(self.user.id), perms.SHOW))
        return acl

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

    @classmethod
    def filter_clinics(cls, search_term, all_clinics):
        if all_clinics:
            #filter all clinics
            clinics = DBSession.query(Clinic).filter(Clinic.name.ilike('%'+search_term+'%')).all()
        else:
            #filter unassigned clinics
            clinics = DBSession.query(Clinic).outerjoin(user_clinics).filter(
                user_clinics.columns.clinic_id == None, Clinic.name.ilike('%'+search_term+'%')).all()
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
                    'num_pending_responses': 
                        constants.RECOMMENDED_SAMPLE_FRAME[client_tool_id]
                        - num_responses
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


class SubmissionHandlerError(Exception):
    pass


class ZeroSubmissionHandlersError(SubmissionHandlerError):
    pass


class MultipleSubmissionHandlersError(SubmissionHandlerError):
    pass


class ClinicNotFound(SubmissionHandlerError):
    pass


class UserNotFound(SubmissionHandlerError):
    pass


class BaseSubmissionHandler(object):
    def __init__(self, submission):
        self.submission = submission

    def handle_submission(self):  # pragma: no cover
        raise NotImplementedError("handle_submission is not implemented")


class ClinicReportHandler(BaseSubmissionHandler):
    @classmethod
    def parse_data(cls, raw_data):
        # split characteristic on [space] for multiple characteristic
        # submissions
        characteristics = raw_data.get(
            constants.CHARACTERISTIC, '').split(" ")
        return (raw_data.get(constants.CLINIC_IDENTIFIER),
                characteristics,
                raw_data.get(constants.XFORM_ID),)

    def handle_submission(self):
        clinic_code, characteristics, xform_id = \
            ClinicReportHandler.parse_data(self.submission.raw_data)

        # check if we have a valid clinic with said id
        try:
            clinic = Clinic.get(Clinic.code == clinic_code)
        except NoResultFound:
            raise ClinicNotFound
        else:
            for characteristic in characteristics:
                clinic_submission = ClinicSubmission(
                    clinic_id=clinic.id,
                    submission=self.submission,
                    characteristic=characteristic,
                    xform_id=xform_id
                )
                DBSession.add(clinic_submission)


class ClinicRegistrationHandler(BaseSubmissionHandler):
    @classmethod
    def parse_data(cls, raw_data):
        """
        Return the user_id and the clinic's name
        """
        return (raw_data.get(constants.USER_ID),
                raw_data.get(constants.CLINIC_NAME))

    def handle_submission(self):
        user_id, clinic_name = ClinicRegistrationHandler.parse_data(
            self.submission.raw_data)

        clinic = Clinic(
            name=clinic_name,
            code='{}'.format(random.randint(189, 1287190)))

        # check is user exists
        user = None
        try:
            user = User.get(User.id == user_id)
        except NoResultFound:
            pass
        else:
            clinic.user = user
        finally:
            DBSession.add(clinic)
            # flush to get the clinic's id
            DBSession.flush()
            clinic.code = hashid.encrypt(clinic.id)

        # if no user, raise UserNotFound
        if user is None:
            raise UserNotFound("User with id {} was not found".format(user_id))


def determine_handler_class(submission, mapping):
    """
    Determine the handler to use to handle the submission
    """
    try:
        xform_id = submission.raw_data[constants.XFORM_ID]
    except KeyError:
        raise SubmissionHandlerError(
            "'{}' not found in json".format(constants.XFORM_ID))

    # for each item in mapping check if this id exists
    handlers = filter(lambda x: xform_id in x[1], mapping)

    if len(handlers) == 1:
        handler_class, xform_ids = handlers[0]
        return handler_class
    elif len(handlers) == 0:
        raise ZeroSubmissionHandlersError(
            "No handlers found for '{}'".format(xform_id))
    else:
        raise MultipleSubmissionHandlersError(
            "Multiple handlers found for '{}'".format(xform_id))


class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True)
    raw_data = Column(JSON, nullable=False)

    # tools to handler mapping
    HANDLER_TO_XFORMS_MAPPING = (
        (ClinicReportHandler,
         [tool for tool, label in constants.CLIENT_TOOLS]),
        (ClinicRegistrationHandler, [constants.CLINIC_REGISTRATION]),
    )

    @classmethod
    def create_from_json(cls, payload):
        # TODO: check for and handle json.loads parse errors
        submission = Submission(raw_data=json.loads(payload))
        DBSession.add(submission)

        # TODO: handle duplicates within handlers, via uuid
        handler_class = determine_handler_class(
            submission, cls.HANDLER_TO_XFORMS_MAPPING)
        handler_class(submission).handle_submission()
        return submission


class ReportingPeriod(Base):
    __tablename__ = 'reporting_periods'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    start_date = Column(Date(), nullable=False)
    end_date = Column(Date(), nullable=False)
