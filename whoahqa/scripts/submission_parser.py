import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from whoahqa.constants import characteristics as constants
from whoahqa.models import (
    Base,
    DBSession,
    ClinicSubmission,
    Municipality)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    parse_municipalities_from_submissions()


def parse_municipalities_from_submissions():
    clinic_submissions = ClinicSubmission.all()
    for clinic_submission in clinic_submissions:
        clinic = clinic_submission.clinic
        if clinic.municipality is None:
            with transaction.manager:
                try:
                    municipality_name = clinic_submission.submission.raw_data[
                        constants.MUNICIPALITY_IDENTIFIER]

                    municipality_params = {'name': municipality_name}
                    municipality = Municipality.get_or_create(
                        Municipality.name == municipality_name,
                        **municipality_params)

                    clinic.municipality = municipality
                    DBSession.add_all([municipality, clinic])

                except KeyError:
                    pass
