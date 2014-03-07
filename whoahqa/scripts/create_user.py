import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from whoahqa.security import pwd_context
from whoahqa.models import (
    DBSession,
    Base,
    User,
    UserProfile,
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <username> <password>\n'
          '(example: "%s development.ini bob bob1")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 4:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    pwd_context.load_path(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    username = argv[2]
    password = argv[3]
    with transaction.manager:
        profile = UserProfile(
            user=User(), username=username, password=password)
        DBSession.add(profile)
