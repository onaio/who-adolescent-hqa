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

ONE = 'one'
TWO = 'two'
THREE = 'three'
FOUR = 'four'
FIVE = 'five'
SIX = 'six'
SEVEN = 'seven'
EIGHT = 'eight'
NINE = 'nine'
TEN = 'ten'
ELEVEN = 'eleven'
TWELVE = 'twelve'
THIRTEEN = 'thirteen'
FOURTEEN = 'fourteen'
FIFTEEN = 'fifteen'
SIXTEEN = 'sixteen'
SEVENTEEN = 'seventeen'
EIGHTEEN = 'eighteen'
NINETEEN = 'nineteen'
TWENTY = 'twenty'

CHARACTERISTICS = [
    (ONE, u"Policies and procedures are in place that do not restrict the "
          u" provision of health services on any terms"),
    (TWO, u"Health-care providers treat all adolescent clients with equal"
          u" care and respect, regardless of status"),
    (THREE, u"Support staff treat all adolescent clients with equal care"
            u" and respect, regardless of status"),
    (FOUR, u"Policies and procedures are in place that ensure that health"
           u" services are either free or affordable to adolescents"),
    (FIVE, u"The point of health service delivery has convenient hours of"
           u" operation"),
    (SIX, u"Adolescents are well-informed about the range of available"
          u" reproductive health services and how to obtain them"),
    (SEVEN, u"Community members understand the benefits that adolescents"
            u" will gain by obtaining the health services they need,"
            u" and support their provision"),
    (EIGHT, u"Some health services and health-related commodities are"
            u" provided to adolescents in the community by selected"
            u" community members, outreach workers and adolescents"
            u" themselves"),
    (NINE, u"Policies and procedures are in place that guarantee client"
           u" confidentiality"),
    (TEN, u"The point of health service delivery ensures privacy"),
    (ELEVEN, u"Health-care providers are non-judgemental, considerate and"
             u" easy to relate to"),
    (TWELVE, u"The point of health service delivery ensures consultations"
             u" occur in a short waiting time. with or without an"
             u" appointment, and (where necessary) with referral"),
    (THIRTEEN, u"The point of health service delivery has an appealing"
               u" and clean environment"),
    (FOURTEEN, u"The point of health service delivery provides information"
               u" and education through a variety of channels"),
    (FIFTEEN, u"Adolescents are actively involved in designing, assessing"
              u" and providing health services"),
    (SIXTEEN, u"The required package of health care is provided to fulfil"
              u" the needs of all adolescents either at the point of health"
              u" service delivery or through referral linkages"),
    (SEVENTEEN, u"Health-care providers have the required competencies to"
                u" work with adolescents and to provide them with the"
                u" required health services"),
    (EIGHTEEN, u"Health-care providers use evidence-based protocols and"
               u" guidelines to provide health services"),
    (NINETEEN, u"Health-care providers are able to dedicate sufficient time"
               u" to work effectively with their adolescent clients"),
    (TWENTY, u"The point of health service delivery has the required"
             u" equipment, supplies and basic services necessary to deliver"
             u" the required health services")
]

CHARACTERISTIC_MAPPING = {
    ONE: {
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
    },
    TWO: {
        ADOLESCENT_CLIENT: (
            'characteristic_two/ch2_q1',
            'characteristic_two/ch2_q2'
        ),
        HEALTH_CARE_PROVIDER: (
            'characteristic_two/ch2_q1',
        ),
        ADOLESCENT_IN_COMMUNITY: (
            'characteristic_two/ch2_q1',
        )
    },
    THREE: {
        ADOLESCENT_CLIENT: (
            'characteristic_three/ch3_q1',
            'characteristic_three/ch3_q2',
            'characteristic_three/ch3_q3',
            'characteristic_three/ch3_q4'
        ),
        SUPPORT_STAFF: {
            'characteristic_three/ch3_q1',
        },
        ADOLESCENT_IN_COMMUNITY: {
            'characteristic_three/ch3_q1',
        }
    },
    FOUR: {
        ADOLESCENT_CLIENT: (
            'characteristic_four/ch4_q1',
            'characteristic_four/ch4_q2',
            'characteristic_four/ch4_q3'
        ),
        HEALTH_FACILITY_MANAGER: {
            'characteristic_four/ch4_q1',
            'characteristic_four/ch4_q2'
        },
        ADOLESCENT_IN_COMMUNITY: {
            'characteristic_four/ch4_q1'
        }
    },
    FIVE: {
        ADOLESCENT_CLIENT: (
            'characteristic_five/ch5_q1',
        ),
        HEALTH_FACILITY_MANAGER: {
            'characteristic_five/ch5_q1',
        },
        ADOLESCENT_IN_COMMUNITY: {
            'characteristic_five/ch5_q1',
        }
    },
    SIX: {
        ADOLESCENT_CLIENT: {
            'characteristic_six/ch6_q1',
        },
        ADOLESCENT_IN_COMMUNITY: {
            'characteristic_six/ch6_q1',
        }
    },
    SEVEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_seven/ch7_q1',
            'characteristic_seven/ch7_q2',
            'characteristic_seven/ch7_q3'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_seven/ch7_q1',
        },
        COMMUNITY_MEMBER: {
            'characteristic_seven/ch7_q1',
            'characteristic_seven/ch7_q2',
            'characteristic_seven/ch7_q3',
            'characteristic_seven/ch7_q4'
        },
        ADOLESCENT_IN_COMMUNITY: {
            'characteristic_seven/ch7_q1',
            'characteristic_seven/ch7_q2',
            'characteristic_seven/ch7_q3'
        }
    },
    EIGHT: {
        ADOLESCENT_CLIENT: {
            'characteristic_eight/ch8_q1'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_eight/ch8_q1'
        },
        OUTREACH_WORKER: {
            'characteristic_eight/ch8_q1',
        },
        ADOLESCENT_IN_COMMUNITY: {
            'characteristic_eight/ch8_q1',
            'characteristic_eight/ch8_q2'
        }
    },
    NINE: {
        ADOLESCENT_CLIENT: {
            'characteristic_nine/ch9_q1',
            'characteristic_nine/ch9_q2',
            'characteristic_nine/ch9_q3',
            'characteristic_nine/ch9_q4'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_nine/ch9_q1'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_nine/ch9_q1'
        },
        OBSERVATION_GUIDE: {
            'characteristic_nine/ch9_q1'
        }
    },
    TEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_ten/ch10_q1',
            'characteristic_ten/ch10_q2',
            'characteristic_ten/ch10_q3',
            'characteristic_ten/ch10_q4'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_ten/ch10_q1',
            'characteristic_ten/ch10_q2'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_ten/ch10_q1'
        },
        OBSERVATION_GUIDE: {
            'characteristic_ten/ch10_q1',
            'characteristic_ten/ch10_q2',
            'characteristic_ten/ch10_q3'
        }
    },
    ELEVEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_eleven/ch11_q1',
            'characteristic_eleven/ch11_q2',
            'characteristic_eleven/ch11_q3',
            'characteristic_eleven/ch11_q4'
        },
        OBSERVATION_GUIDE: {
            'characteristic_eleven/ch11_q1',
            'characteristic_eleven/ch11_q2',
            'characteristic_eleven/ch11_q3',
            'characteristic_eleven/ch11_q4'
        }
    },
    TWELVE: {
        ADOLESCENT_CLIENT: {
            'characteristic_twelve/ch12_q1',
            'characteristic_twelve/ch12_q2',
            'characteristic_twelve/ch12_q3'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_twelve/ch12_q1',
            'characteristic_twelve/ch12_q2'
        },
        SUPPORT_STAFF: {
            'characteristic_twelve/ch12_q1',
            'characteristic_twelve/ch12_q2',
        },
        OBSERVATION_GUIDE: {
            'characteristic_twelve/ch12_q1'
        }
    },
    THIRTEEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_thirteen/ch13_q1',
            'characteristic_thirteen/ch13_q2',
            'characteristic_thirteen/ch13_q3',
            'characteristic_thirteen/ch13_q4',
            'characteristic_thirteen/ch13_q5',
            'characteristic_thirteen/ch13_q6'
        },
        OBSERVATION_GUIDE: {
            'characteristic_thirteen/ch13_q1',
            'characteristic_thirteen/ch13_q2',
            'characteristic_thirteen/ch13_q3',
            'characteristic_thirteen/ch13_q4',
            'characteristic_thirteen/ch13_q5',
            'characteristic_thirteen/ch13_q6',
            'characteristic_thirteen/ch13_q7',
            'characteristic_thirteen/ch13_q8',
            'characteristic_thirteen/ch13_q9'
        }
    },
    FOURTEEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_fourteen/ch14_q1',
            'characteristic_fourteen/ch14_q2',
            'characteristic_fourteen/ch14_q3',
            'characteristic_fourteen/ch14_q4'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_fourteen/ch14_q1'
        },
        OBSERVATION_GUIDE: {
            'characteristic_fourteen/ch14_q1',
            'characteristic_fourteen/ch14_q2'
        }
    },
    FIFTEEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_fifteen/ch15_q1',
            'characteristic_fifteen/ch15_q2'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_fifteen/ch15_q1',
            'characteristic_fifteen/ch15_q2'
        }
    },
    SIXTEEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_sixteen/ch16_q1',
            'characteristic_sixteen/ch16_q2'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_sixteen/ch16_q1',
            'characteristic_sixteen/ch16_q2',
            'characteristic_sixteen/ch16_q3',
            'characteristic_sixteen/ch16_q4',
            'characteristic_sixteen/ch16_q5',
            'characteristic_sixteen/ch16_q6',
            'characteristic_sixteen/ch16_q7',
            'characteristic_sixteen/ch16_q8',
            'characteristic_sixteen/ch16_q9',
            'characteristic_sixteen/ch16_q10',
            'characteristic_sixteen/ch16_q11',
            'characteristic_sixteen/ch16_q12',
            'characteristic_sixteen/ch16_q13',
            'characteristic_sixteen/ch16_q14'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_sixteen/ch16_q1',
            'characteristic_sixteen/ch16_q2',
            'characteristic_sixteen/ch16_q3',
            'characteristic_sixteen/ch16_q4',
            'characteristic_sixteen/ch16_q5',
            'characteristic_sixteen/ch16_q6',
            'characteristic_sixteen/ch16_q7',
            'characteristic_sixteen/ch16_q8',
            'characteristic_sixteen/ch16_q9',
            'characteristic_sixteen/ch16_q10',
            'characteristic_sixteen/ch16_q11',
            'characteristic_sixteen/ch16_q12',
            'characteristic_sixteen/ch16_q13',
            'characteristic_sixteen/ch16_q14'
        }
    },
    SEVENTEEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_seventeen/ch17_q1',
            'characteristic_seventeen/ch17_q2',
            'characteristic_seventeen/ch17_q3',
            'characteristic_seventeen/ch17_q4',
            'characteristic_seventeen/ch17_q5',
            'characteristic_seventeen/ch17_q6'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_seventeen/ch17_q1',
            'characteristic_seventeen/ch17_q2',
            'characteristic_seventeen/ch17_q3',
            'characteristic_seventeen/ch17_q4',
            'characteristic_seventeen/ch17_q5',
            'characteristic_seventeen/ch17_q6',
            'characteristic_seventeen/ch17_q7',
            'characteristic_seventeen/ch17_q8',
            'characteristic_seventeen/ch17_q9',
            'characteristic_seventeen/ch17_q10',
            'characteristic_seventeen/ch17_q11',
            'characteristic_seventeen/ch17_q12',
            'characteristic_seventeen/ch17_q13',
            'characteristic_seventeen/ch17_q14',
            'characteristic_seventeen/ch17_q15'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_seventeen/ch17_q1',
            'characteristic_seventeen/ch17_q2',
            'characteristic_seventeen/ch17_q3',
            'characteristic_seventeen/ch17_q4',
            'characteristic_seventeen/ch17_q5',
            'characteristic_seventeen/ch17_q6',
            'characteristic_seventeen/ch17_q7',
            'characteristic_seventeen/ch17_q8',
            'characteristic_seventeen/ch17_q9',
            'characteristic_seventeen/ch17_q10',
            'characteristic_seventeen/ch17_q11',
            'characteristic_seventeen/ch17_q12',
            'characteristic_seventeen/ch17_q13'
        },
        OBSERVATION_GUIDE: {
            'characteristic_seventeen/ch17_q1',
            'characteristic_seventeen/ch17_q2',
            'characteristic_seventeen/ch17_q3',
            'characteristic_seventeen/ch17_q4',
            'characteristic_seventeen/ch17_q5',
            'characteristic_seventeen/ch17_q6',
            'characteristic_seventeen/ch17_q7',
            'characteristic_seventeen/ch17_q8',
            'characteristic_seventeen/ch17_q9',
            'characteristic_seventeen/ch17_q10',
            'characteristic_seventeen/ch17_q11',
            'characteristic_seventeen/ch17_q12',
            'characteristic_seventeen/ch17_q13',
            'characteristic_seventeen/ch17_q14',
            'characteristic_seventeen/ch17_q15',
            'characteristic_seventeen/ch17_q16',
            'characteristic_seventeen/ch17_q17'
        }
    },
    EIGHTEEN: {
        HEALTH_CARE_PROVIDER: {
            'characteristic_eighteen/ch18_q1',
            'characteristic_eighteen/ch18_q2',
            'characteristic_eighteen/ch18_q3',
            'characteristic_eighteen/ch18_q4',
            'characteristic_eighteen/ch18_q5',
            'characteristic_eighteen/ch18_q6',
            'characteristic_eighteen/ch18_q7',
            'characteristic_eighteen/ch18_q8',
            'characteristic_eighteen/ch18_q9',
            'characteristic_eighteen/ch18_q10',
            'characteristic_eighteen/ch18_q11',
            'characteristic_eighteen/ch18_q12',
            'characteristic_eighteen/ch18_q13'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_eighteen/ch18_q1',
            'characteristic_eighteen/ch18_q2',
            'characteristic_eighteen/ch18_q3',
            'characteristic_eighteen/ch18_q4',
            'characteristic_eighteen/ch18_q5',
            'characteristic_eighteen/ch18_q6',
            'characteristic_eighteen/ch18_q7',
            'characteristic_eighteen/ch18_q8',
            'characteristic_eighteen/ch18_q9',
            'characteristic_eighteen/ch18_q10',
            'characteristic_eighteen/ch18_q11',
            'characteristic_eighteen/ch18_q12',
            'characteristic_eighteen/ch18_q13'
        },
        OBSERVATION_GUIDE: {
            'characteristic_eighteen/ch18_q1',
            'characteristic_eighteen/ch18_q2',
            'characteristic_eighteen/ch18_q3',
            'characteristic_eighteen/ch18_q4',
            'characteristic_eighteen/ch18_q5',
            'characteristic_eighteen/ch18_q6',
            'characteristic_eighteen/ch18_q7',
            'characteristic_eighteen/ch18_q8',
            'characteristic_eighteen/ch18_q9',
            'characteristic_eighteen/ch18_q10',
            'characteristic_eighteen/ch18_q11',
            'characteristic_eighteen/ch18_q12',
            'characteristic_eighteen/ch18_q13'
        }
    },
    NINETEEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_nineteen/ch19_q1',
            'characteristic_nineteen/ch19_q2'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_nineteen/ch19_q1',
            'characteristic_nineteen/ch19_q2'
        }
    },
    TWENTY: {
        ADOLESCENT_CLIENT: {
            'characteristic_twenty/ch20_q1'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_twenty/ch20_q1',
            'characteristic_twenty/ch20_q2',
            'characteristic_twenty/ch20_q3',
            'characteristic_twenty/ch20_q4'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_twenty/ch20_q1',
            'characteristic_twenty/ch20_q2',
            'characteristic_twenty/ch20_q3'
        },
        OBSERVATION_GUIDE: {
            'characteristic_twenty/ch20_q1',
            'characteristic_twenty/ch20_q2'
        }
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
        Calculate the aggregate score and the no. of respondents for the
        characteristic/xform_id pair
        """
        # get the questions in this client tool for this characteristic
        question_xpaths = CHARACTERISTIC_MAPPING[characteristic][xform_id]

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

        for characteristic, label in CHARACTERISTICS:
            scores[characteristic] = {}
            scores[characteristic]['totals'] = {
                'total_scores': 0.0,
                'total_questions': 0,
                'total_responses': 0,
                'total_percentage': 0
            }
            mapping = CHARACTERISTIC_MAPPING[characteristic]
            for client_tool_id, questions in mapping.items():
                aggregate_score, num_responses = self.calculate_score(
                    characteristic, client_tool_id)
                stats = {
                    'aggregate_score': aggregate_score if aggregate_score
                    is not None else "-",
                    'num_responses': num_responses,
                    'num_questions': len(questions),
                }
                scores[characteristic][client_tool_id] = stats

                # increment total if value is not None
                if aggregate_score is not None:
                    scores[characteristic]['totals']['total_scores'] +=\
                        aggregate_score

                scores[characteristic]['totals']['total_questions'] +=\
                    len(questions)
                scores[characteristic]['totals']['total_responses'] +=\
                    num_responses

            scores[characteristic]['totals']['total_percentage'] =\
                (scores[characteristic]['totals']['total_scores']/
                 float(scores[characteristic]['totals']['total_questions']))\
                * 100

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
        characteristics = json_data.get(CHARACTERISTIC, '').split(" ")
        return (json_data.get('facility_info/clinic_id'),
                characteristics,
                json_data.get('_xform_id_string'),)

