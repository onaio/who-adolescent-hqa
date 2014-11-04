import random
from sqlalchemy.orm.exc import NoResultFound
from whoahqa import constants
from whoahqa.models import (
    DBSession,
    Clinic)

from whoahqa.utils import hashid
random.seed()


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
        from whoahqa.models import ClinicSubmission

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
        from whoahqa.models import User

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
