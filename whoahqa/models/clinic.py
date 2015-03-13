from pyramid.security import (
    Allow)

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    func,
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import select, and_
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import (
    backref,
    relationship)

from whoahqa.constants import characteristics as constants
from whoahqa.constants import permissions as perms
from whoahqa.models import (
    Base,
    BaseModelFactory,
    DBSession,
    ReportingPeriod)

from whoahqa.models.user import user_clinics

from whoahqa.utils import (
    tuple_to_dict_list,
    check_meets_threshold,
)


class ClinicCharacteristics(Base):
    __tablename__ = 'clinic_characteristics'
    clinic_id = Column(Integer,
                       ForeignKey('clinics.id'),
                       primary_key=True)
    characteristic_id = Column(String(100), nullable=False, primary_key=True)
    period_id = Column(Integer, ForeignKey('reporting_periods.id'),
                       nullable=False, primary_key=True)
    pk_clinic_characteristic = PrimaryKeyConstraint(
        clinic_id, characteristic_id, period_id)
    clinic_characteristic = relationship(
        "Clinic",
        single_parent=True,
        backref=backref('characteristics',
                        cascade="all, delete, delete-orphan"))


class Clinic(Base):
    __tablename__ = 'clinics'
    id = Column(Integer, primary_key=True)
    code = Column(String(100), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    date_created = Column(DateTime(timezone=True),
                          server_default=func.now(), nullable=False)
    user = relationship("User",
                        secondary=user_clinics,
                        uselist=False)

    municipality_id = Column(Integer, ForeignKey('locations.id'),
                             nullable=True)

    municipality = relationship("Municipality",
                                lazy='subquery',
                                backref=backref('clinics', order_by=id),
                                primaryjoin="and_(\
                                    Clinic.municipality_id == Location.id)")
    _cached_key_indicators = None

    @property
    def __acl__(self):
        acl = []
        if self.user is not None:
            acl.append((Allow, "u:{}".format(self.user.id),
                        perms.CAN_VIEW_CLINICS))
        return acl

    def __getitem__(self, item):
        # retrieve the reporting period
        try:
            period_id = int(item)
            period = ReportingPeriod.get(ReportingPeriod.id == period_id)
        except (ValueError, NoResultFound):
            raise KeyError
        else:
            period.__parent__ = self
            period.__name__ = item
            return period

    def assign_to(self, user):
        self.user = user
        DBSession.add(self)

    @property
    def is_assigned(self):
        return self.user is not None

    @property
    def appstruct(self):
        return {
            'name': self.name,
            'code': self.code,
            'municipality': self.municipality_id
        }

    def update(self, name, code, municipality):
        self.name = name
        self.code = code
        self.municipality = municipality

        self.save()

    def get_url(self, request, period):
        return request.route_url('clinics',
                                 traverse=(self.id, period.id))

    @classmethod
    def get_unassigned(cls):
        clinics = DBSession.query(Clinic).outerjoin(user_clinics).filter(
            user_clinics.columns.clinic_id.is_(None)).all()
        return clinics

    @classmethod
    def filter_clinics(cls, search_term, all_clinics):
        if all_clinics:
            # filter all clinics
            clinics = DBSession\
                .query(Clinic)\
                .filter(Clinic.name.ilike('%' + search_term + '%')).all()
        else:
            # filter unassigned clinics
            clinics = DBSession\
                .query(Clinic)\
                .outerjoin(user_clinics)\
                .filter(
                    user_clinics.columns.clinic_id.is_(None),
                    Clinic.name.ilike('%' + search_term + '%')).all()
        return clinics

    def get_num_responses_per_tool(self):
        clinic_submissions_table = Base.metadata.tables['clinic_submissions']
        responses_per_tool = {}
        for tool, sample_frame in \
                constants.RECOMMENDED_SAMPLE_FRAMES.iteritems():
            responses_per_tool[tool] = {
                'sample_frame': sample_frame,
                'responses': (
                    DBSession.query(clinic_submissions_table).filter(
                        and_(
                            clinic_submissions_table.c.clinic_id == self.id,
                            clinic_submissions_table.c.xform_id == tool))
                    .distinct(clinic_submissions_table.c.submission_id)
                    .count())
            }
        return responses_per_tool

    def get_num_responses_per_characteristic_xform_id(self, period):
        clinic_submissions_table = Base.metadata.tables['clinic_submissions']
        result = DBSession.execute(
            select([
                'COUNT(*)',
                clinic_submissions_table.c.characteristic,
                clinic_submissions_table.c.xform_id])
            .select_from(clinic_submissions_table)
            .where(and_(
                clinic_submissions_table.c.clinic_id == self.id,
                clinic_submissions_table.c.period == period))
            .group_by(
                clinic_submissions_table.c.characteristic,
                clinic_submissions_table.c.xform_id)
        ).fetchall()
        return tuple_to_dict_list(
            ('count', 'characteristic', 'xform_id'), result)

    # TODO: factor in reporting period
    def get_period_clinic_submissions(self, period):
        from whoahqa.models import ClinicSubmission, Submission
        return DBSession\
            .query(ClinicSubmission, Submission)\
            .outerjoin(Submission)\
            .filter(ClinicSubmission.clinic_id == self.id,
                    ClinicSubmission.period == period)\
            .all()

    @classmethod
    def calculate_aggregate_scores(
            cls, xpaths, num_responses, submission_jsons):
        """ Gets the aggregate score for a client_tool/characteristic pair.

            :param xpaths:
            list of xpaths required to calculate the aggregate score
            e.g.

            .. code-block:: python

            ['characteristic_one/ch1_q1', 'characteristic_one/ch1_q2']

            :param num_responses
            The number of submissions for the current interviewee group e.g.
            Adolescent client. Should be retrieved by doing an SQL count on
            the `clinic_submissions` table by client_tool/characteristic pair

            :param submission_jsons
            A list of submission json data for the characteristic we are
            interested in. Should be filtered by clinic and reporting period.
        """
        # raise ValueError if num_submissions is invalid
        if int(num_responses) < 1:
            raise ValueError("cant calculate scores with zero responses")

        # for each xpath, loop through the submissions  to find where the
        # value is
        denominator = float(num_responses)
        aggregate_score = 0.0
        for xpath in xpaths:
            num_1s = float(
                len(filter(
                    lambda s: s.get(xpath, '0') == '1', submission_jsons)))
            aggregate_score += num_1s / denominator
        return aggregate_score

    def get_scores(self):  # , period):
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
                    'total_responses': 4,
                    'total_percentage': [0-100],
                    'meets_threshold': True|False,
                    'score_classification': great|good|bad
                }
            }
        }
        """
        # get the number of responses per characteristic and xform_id pair for
        # this clinic
        characteristic_xforms =\
            self.get_num_responses_per_characteristic_xform_id(self.id)

        # get all submissions for this clinic and specified period
        submissions = self.get_period_clinic_submissions()

        scores = {}

        for characteristic, label, number in constants.CHARACTERISTICS:
            scores[characteristic] = {}
            total_scores = 0
            total_questions = 0
            total_responses = 0
            mapping = constants.CHARACTERISTIC_MAPPING[characteristic]
            meets_threshold = True
            for client_tool_id, xpaths in mapping.items():
                # filter this clinics submissions to this characteristic and
                # this client_tool
                submission_jsons = [s.raw_data for c, s in submissions
                                    if c.characteristic == characteristic and
                                    c.xform_id == client_tool_id]
                recommended_sample_frame =\
                    constants.RECOMMENDED_SAMPLE_FRAMES[client_tool_id]

                # get the number of responses for this characteristic/xform_id
                current_characteristic_xforms = filter(
                    lambda c: c['characteristic'] == characteristic
                    and c['xform_id'] == client_tool_id,
                    characteristic_xforms)

                num_responses = 0
                if len(current_characteristic_xforms) > 0:
                    # we have responses for this combination
                    num_responses = current_characteristic_xforms[0]['count']

                # check if the number of submissions meets the threshold
                if not check_meets_threshold(
                        num_responses,
                        recommended_sample_frame,
                        constants.MINIMUM_SAMPLE_FRAME_RATIO):
                    meets_threshold = False

                aggregate_score = None

                if num_responses > 0:
                    aggregate_score = Clinic.calculate_aggregate_scores(
                        xpaths, num_responses, submission_jsons)
                    # increment total if value is not None
                    total_scores += aggregate_score

                stats = {
                    'aggregate_score': aggregate_score,
                    'num_responses': num_responses,
                    'num_questions': len(xpaths),
                    'num_pending_responses':
                    recommended_sample_frame - num_responses
                }
                scores[characteristic][client_tool_id] = stats

                total_questions += len(xpaths)
                total_responses += num_responses

            total_percentage = None if total_responses == 0 else (
                total_scores / float(total_questions) * 100)
            scores[characteristic]['totals'] = {
                'total_scores': None if total_scores == 0 else total_scores,
                'total_questions': total_questions,
                'total_responses': total_responses,
                'total_percentage': total_percentage,
                'meets_threshold': meets_threshold,
                'score_classification': constants.get_score_classification(
                    total_percentage)
            }
        return scores

    def activate_characteristic(self, characteristic_id, period_id):
        clinic_characteristic = ClinicCharacteristics(
            clinic_id=self.id, characteristic_id=characteristic_id,
            period_id=period_id)
        DBSession.add(clinic_characteristic)

    def get_active_characteristics(self, period):
        clinic_characteristics = DBSession.query(ClinicCharacteristics)\
            .filter(
                ClinicCharacteristics.clinic_id == self.id,
                ClinicCharacteristics.period_id == period.id).all()
        return clinic_characteristics

    def calculate_key_indicator_scores(self, characteristics_list):
        """
        Calculate the aggregate score for a key indicator eg.
        equitable = {
            'one': x%,
            'two': y%,
            'three': z%
        }
        """
        # get the number of responses per characteristic and xform_id pair for
        # this clinic
        characteristic_xforms_responses =\
            self.get_num_responses_per_characteristic_xform_id(self.id)

        # get all submissions for this clinic and specified period
        submissions = self.get_period_clinic_submissions()

        key_indicator_scores = {}

        for characteristic in characteristics_list:
            mapping = constants.CHARACTERISTIC_MAPPING[characteristic]
            total_responses = 0
            total_scores = 0
            total_questions = 0
            key_indicator_scores[characteristic] = {}
            for client_tool_id, xpaths in mapping.items():
                # filter this clinics submissions to this characteristic and
                # this client_tool
                submission_jsons = [s.raw_data for c, s in submissions
                                    if c.characteristic == characteristic and
                                    c.xform_id == client_tool_id]

                # get the number of responses for this characteristic/xform_id
                current_characteristic_xforms = filter(
                    lambda c: c['characteristic'] == characteristic
                    and c['xform_id'] == client_tool_id,
                    characteristic_xforms_responses)

                num_responses = 0
                if len(current_characteristic_xforms) > 0:
                    # we have responses for this combination
                    num_responses = current_characteristic_xforms[0]['count']

                aggregate_score = None
                if num_responses > 0:
                    aggregate_score = Clinic.calculate_aggregate_scores(
                        xpaths, num_responses, submission_jsons)

                if aggregate_score is not None:
                    total_scores += aggregate_score

                total_responses += num_responses
                total_questions += len(xpaths)

                key_indicator_scores[characteristic] = None\
                    if total_responses == 0 else (
                        total_scores / float(total_questions) * 100)

        return key_indicator_scores

    def get_all_key_indicator_scores(self):
        """
        key_indicator_scores = {
            equitable = {
                'one': x%,
                'two': y%,
                'three': z%,
                'average_score': xyz/3%
                },
            acceptable = {
                'sixteen': z%,
                'average_score': z%
            },
            ...
        }
        """
        key_indicators = tuple_to_dict_list(
            ("key", "characteristic_list"), constants.KEY_INDICATORS)
        all_key_indicator_scores = {}
        for key_char_pair in key_indicators:
            average_score = 0
            indicator_score = self.calculate_key_indicator_scores(
                key_char_pair['characteristic_list'])
            for score in indicator_score.itervalues():
                if score is not None:
                    average_score += score
            all_key_indicator_scores[key_char_pair['key']] = indicator_score
            all_key_indicator_scores[key_char_pair['key']].update(
                {
                    'average_score': (average_score / len(indicator_score))
                }
            )

        return all_key_indicator_scores

    def key_indicators(self, period):
        from whoahqa.models import ClinicReport
        if self._cached_key_indicators is None:
            report = ClinicReport.get_or_generate(self, period)
            self._cached_key_indicators = report.get_key_indicators()

        return self._cached_key_indicators


class ClinicFactory(BaseModelFactory):

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
