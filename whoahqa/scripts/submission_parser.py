import os
import sys
import transaction

from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from whoahqa.constants import characteristics as constants
from whoahqa.models import (
    Base,
    Clinic,
    DBSession,
    Submission,
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
    submissions = Submission.all()
    for submission in submissions:
        try:
            with transaction.manager:
                clinic_code = submission.raw_data[constants.CLINIC_IDENTIFIER]
                clinic = Clinic.get(
                    Clinic.code == clinic_code)

                municipality_name = submission.raw_data[
                    constants.MUNICIPALITY_IDENTIFIER]

                municipality_params = {'name': municipality_name}
                municipality = Municipality.get_or_create(
                    Municipality.name == municipality_name,
                    **municipality_params)

                if clinic.municipality is None:
                    clinic.municipality = municipality
                    DBSession.add_all([municipality, clinic])

        except (NoResultFound, KeyError):
            pass
