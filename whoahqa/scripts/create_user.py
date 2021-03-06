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
    Group,
    OnaUser,
    User,
    UserProfile,
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <username> <password>\n'
          '(example: "%s development.ini bob bob1")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 5:
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
    group = argv[4]
    with transaction.manager:
        group_criteria = Group.name == group
        group_params = {'name': group}
        group = Group.get_or_create(
            group_criteria,
            **group_params)

        user = User()
        user.group = group
        profile = UserProfile(
            user=user, username=username, password=password)
        ona_user_params = {
            'user': user,
            'username': username,
            'refresh_token': 'test'}
        ona_user = OnaUser.get_or_create(
            OnaUser.username == username,
            **ona_user_params)
        DBSession.add_all([user, profile, ona_user])
