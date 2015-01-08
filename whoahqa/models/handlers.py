from sqlalchemy.orm.exc import NoResultFound
from whoahqa.constants import characteristics as constants
from whoahqa.models import (
    DBSession,
    Clinic,
    Municipality,
    State)


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
        Return map containing:
            - user_id
            - clinic's name
            - clinic identifier
            - municipality name
            - state name
        """
        return {
            'user_id': raw_data.get(constants.USER_ID),
            'clinic_name': raw_data.get(constants.CLINIC_NAME),
            'clinic_code': raw_data.get(constants.CLINIC_IDENTIFIER),
            'municipality_name': raw_data.get(
                constants.MUNICIPALITY_IDENTIFIER),
            'state_name': raw_data.get(constants.STATE_IDENTIFIER)
        }

    def handle_submission(self):
        from whoahqa.models import User

        map_data = ClinicRegistrationHandler.parse_data(
            self.submission.raw_data)

        state_args = {'name': map_data['state_name']}

        state = State(State.name == state_args['name'], **state_args)

        municipality_args = {'name': map_data['municipality_name'],
                             'parent': state}
        municipality = Municipality.get_or_create(
            Municipality.name == map_data['municipality_name'],
            **municipality_args)

        clinic = Clinic(
            name=map_data['clinic_name'],
            code=map_data['clinic_code'],
            municipality=municipality)

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
            municipality.save()

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
