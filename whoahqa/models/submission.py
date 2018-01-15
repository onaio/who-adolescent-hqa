import json
import itertools

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    ForeignKey,
    String
)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.dialects.postgresql import JSON

from whoahqa.constants import characteristics as constants
from whoahqa.models import (
    Base,
    BaseModelFactory,
    ClinicRegistrationHandler,
    ClinicReportHandler,
    DBSession,
    MultipleSubmissionHandlersError,
    SubmissionHandlerError,
    ZeroSubmissionHandlersError)


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
        (ClinicReportHandler, [
            tool
            for tool, _ in itertools.chain(
                constants.CLIENT_TOOLS,
                constants.CLIENT_TOOLS_V2)]),
        (ClinicRegistrationHandler, [constants.CLINIC_REGISTRATION]),
    )

    @classmethod
    def create_from_json(cls, payload):
        # TODO: check for and handle json.loads parse errors
        if type(payload) is not dict:
            payload = json.loads(payload)

        submission = None

        if payload.get(constants.DEPRECATED_ID, None):
            # add or update existing submission
            try:
                submission = Submission.get(
                    Submission.raw_data[constants.INSTANCE_ID].astext ==
                    payload[constants.DEPRECATED_ID])

                submission.raw_data = payload
                DBSession.add(submission)
            except NoResultFound:
                submission = Submission(raw_data=payload)
                DBSession.add(submission)

        elif not Submission.exists(payload):
            submission = Submission(raw_data=payload)
            DBSession.add(submission)

        handler_class = determine_handler_class(
            submission, cls.HANDLER_TO_XFORMS_MAPPING)
        handler_class(submission).handle_submission()

        return submission

    @classmethod
    def exists(cls, payload):
        try:
            Submission.get(
                Submission.raw_data[constants.UUID].astext ==
                payload[constants.UUID])
            return True
        except NoResultFound:
            return False


class ClinicSubmission(Base):
    __tablename__ = 'clinic_submissions'
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    submission_id = Column(
        Integer, ForeignKey('submissions.id'), primary_key=True)
    characteristic = Column(String, nullable=False, primary_key=True)
    xform_id = Column(String, nullable=False, primary_key=True)
    submission = relationship("Submission", lazy='subquery')
    period = Column(String, nullable=True)
    valid = Column(Boolean, default=True)
    clinic = relationship(
        "Clinic",
        lazy='subquery',
        backref=backref("submissions", cascade="all, delete, delete-orphan"))


class SubmissionFactory(BaseModelFactory):
    __acl__ = []

    def __getitem__(self, item):  # pragma: no cover
        raise NotImplementedError
