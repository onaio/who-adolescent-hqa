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
from sqlalchemy.sql.expression import true
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

        if self.municipality:
            municipality_user = self.municipality.user

            if municipality_user:
                acl.append((Allow, "u:{}".format(municipality_user.id),
                            perms.CAN_VIEW_CLINICS))

            if self.municipality.parent:
                state_user = self.municipality.parent.user

                if state_user:
                    acl.append((Allow, "u:{}".format(state_user.id),
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

    def get_num_responses_per_tool(self, period):
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
                            clinic_submissions_table.c.valid == true(),
                            clinic_submissions_table.c.xform_id == tool,
                            clinic_submissions_table.c.period == period))
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
                clinic_submissions_table.c.valid == true(),
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
                    ClinicSubmission.period == period,
                    ClinicSubmission.valid == true())\
            .all()

    def calculate_characteristic_aggregate_scores(
            self, xpath, num_responses, submission_jsons):
        """ Gets the aggregate score for a client_tool/characteristic pair.

            :param xpath:
            the total score xpath for the characteristic
            e.g.

            .. code-block:: python

            'characteristic_one/ch1_scores'

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
        def get_score(s):
            try:
                return int(s.get(xpath, 0))
            except ValueError:
                return 0

        denominator = float(num_responses)
        aggregate_score = 0.0
        total_score = sum(map(get_score, submission_jsons))
        aggregate_score = total_score / denominator
        return aggregate_score

    def get_scores(self, period):
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

        submissions = self.get_period_clinic_submissions(period)

        # filter count based on whether score is valid
        characteristics_submission_map = \
            self.get_num_responses_per_characteristic_xform_id(period)

        scores = {}

        for characteristic, label, number in constants.CHARACTERISTICS:
            scores[characteristic] = {}
            total_scores = 0
            total_questions = 0
            total_responses = 0
            total_pending_responses = 0

            mapping = constants.CHARACTERISTIC_MAPPING[characteristic]
            meets_threshold = True

            for score_xpath, client_tools in mapping.items():
                # generate characteristic tool scores
                for client_tool_id in client_tools:
                    recommended_sample_frame =\
                        constants.RECOMMENDED_SAMPLE_FRAMES[client_tool_id]
                    num_questions = (constants.QUESTION_COUNT
                                     [characteristic][client_tool_id])

                    submission_jsons = [s.raw_data
                                        for c, s in submissions
                                        if c.characteristic == characteristic
                                        and c.xform_id == client_tool_id]

                    current_submission_map = filter(
                        lambda c: c['characteristic'] == characteristic
                        and c['xform_id'] == client_tool_id,
                        characteristics_submission_map)

                    num_responses = 0

                    if len(current_submission_map) > 0:
                        # we have responses for this combination
                        num_responses = current_submission_map[0]['count']

                    # check if number of submissions meets the threshold
                    if not check_meets_threshold(
                            num_responses,
                            recommended_sample_frame,
                            constants.MINIMUM_SAMPLE_FRAME_RATIO):
                        meets_threshold = False

                    aggregate_score = None

                    if num_responses > 0:
                        # filter out submissions with invalid characteristic
                        # data
                        valid_submissions = filter(
                            lambda s: not bool(int(
                                s[constants.INVALID_CHARACTERISTICS_FLAGS
                                    [characteristic]])),
                            submission_jsons)
                        aggregate_score =\
                            self.calculate_characteristic_aggregate_scores(
                                score_xpath, num_responses, valid_submissions)
                        # increment total scores
                        total_scores += aggregate_score

                    num_pending_responses = (
                        recommended_sample_frame - num_responses)
                    stats = {
                        'aggregate_score': aggregate_score,
                        'num_responses': num_responses,
                        'num_questions': num_questions,
                        'num_pending_responses': num_pending_responses
                    }

                    scores[characteristic][client_tool_id] = stats
                    total_questions += num_questions
                    total_responses += num_responses
                    total_pending_responses += num_pending_responses

            total_percentage = None if total_responses == 0 else (
                total_scores / float(total_questions) * 100)

            scores[characteristic]['totals'] = {
                'total_scores': None if total_scores == 0 else total_scores,
                'total_questions': total_questions,
                'total_responses': total_responses,
                'total_pending_responses': total_pending_responses,
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

    def get_key_indicator_scores(self, period):
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
        key_indicators = {key: list(values)
                          for key, values in constants.KEY_INDICATORS}
        key_indicator_scores = {}

        scores = self.get_scores(period)

        for key_indicator, characteristic_list in key_indicators.iteritems():
            total_scores = 0
            characteristic_scores = [scores[k]
                                     .get('totals')
                                     .get('total_percentage') or 0
                                     for k in characteristic_list]

            total_scores = sum(characteristic_scores)

            key_indicator_scores[key_indicator] = (
                total_scores / len(characteristic_list))

        return key_indicator_scores

    def key_indicators(self, period):
        from whoahqa.models import ClinicReport
        if self._cached_key_indicators is None:
            report = ClinicReport.get_or_generate(self, period)
            self._cached_key_indicators = report.get_key_indicators()

        return self._cached_key_indicators

    def update_reports(self):
        for report in self.reports:
            report.update()


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
