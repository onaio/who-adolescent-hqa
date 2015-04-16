from sqlalchemy.orm.exc import NoResultFound
from whoahqa.constants import characteristics as constants
from whoahqa.models import (
    DBSession,
    Clinic)


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

        # Check if we have a valid clinic with said id
        try:
            clinic = Clinic.get(Clinic.code == clinic_code)
        except NoResultFound:
            raise ClinicNotFound
        else:
            for characteristic in characteristics:
                if characteristic:
                    clinic_submission = ClinicSubmission(
                        clinic_id=clinic.id,
                        submission=self.submission,
                        characteristic=characteristic,
                        xform_id=xform_id,
                        period=(
                            self.submission.raw_data[
                                constants.PERIOD_IDENTIFIER]),
                        valid=(not bool(int(
                            self.submission.raw_data
                            [constants.INVALID_CHARACTERISTICS_FLAGS
                                [characteristic]])))
                    )
                    DBSession.add(clinic_submission)

            clinic.update_reports()


class ClinicRegistrationHandler(BaseSubmissionHandler):

    @classmethod
    def parse_data(cls, raw_data):
        """
        Return map containing:
            - user_id
            - clinic's name
            - clinic identifier
        """
        return {
            'user_id': raw_data.get(constants.USER_ID),
            'clinic_name': raw_data.get(constants.CLINIC_NAME),
            'clinic_code': raw_data.get(constants.CLINIC_IDENTIFIER)
        }

    def handle_submission(self):
        from whoahqa.models import User

        map_data = ClinicRegistrationHandler.parse_data(
            self.submission.raw_data)
        clinic = Clinic(
            name=map_data['clinic_name'],
            code=map_data['clinic_code'])

        # check is user exists
        user = None
        try:
            user = User.get(User.id == map_data['user_id'])
        except NoResultFound:
            pass
        else:
            clinic.user = user
        finally:
            clinic.save()

        # if no user, raise UserNotFound
        if user is None:
            raise UserNotFound("User with id {} was not found".format(
                map_data['user_id']))


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
