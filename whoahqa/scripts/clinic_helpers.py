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
    Clinic,
    ClinicReport)

from whoahqa.models.user import (
    delete_user_clinics,
    user_clinics)


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
    reset_all_clinics()


def reset_all_clinics():
    # delete all Clinics
    with transaction.manager:
        for c in Clinic.all():
            # import ipdb; ipdb.set_trace()
            DBSession.query(ClinicReport).filter_by(clinic_id=c.id).delete()
            delete_user_clinics([c.id for c in Clinic.all()])
            DBSession.query(Clinic).filter_by(id=45).delete()
            DBSession.query(Clinic).join(user_clinics).filter(
                user_clinics.columns.clinic_id == c.id).delete()
            DBSession.commit()
