import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from whoahqa.models import (
    Base,
    DBSession,
    Location)

from whoahqa.models.user import user_locations


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
    reset_all_locations()


def reset_all_locations():
    # delete all Clinics
    user_locations.delete().where(
        user_locations.columns.location_id.in_(Location.all()))
    with transaction.manager:
        for location in Location.all():
            DBSession.delete(location)
