import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging)

from whoahqa.models import (
    DBSession,
    Base,
    State,
    Municipality,
    Clinic
)

from ..utils import normalizeString, UnicodeDictReader


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
    import_health_data()


def import_health_data():
    file_name = os.path.relpath('whoahqa/data/clinics.csv')
    with open(file_name, 'rU') as source:
        rdr = UnicodeDictReader(source)
        existing_states = [normalizeString(state.name)
                           for state in State.all()]
        existing_municipalities = [
            normalizeString(municipality.name)
            for municipality in Municipality.all()]
        existing_clinics = [clinic.code for clinic in Clinic.all()]

        with transaction.manager:
            for row in rdr:
                state = None
                municipality = None
                normalized_state = normalizeString(row['state'])
                normalized_municipality = normalizeString(
                    row['municipality'])

                if normalized_state not in existing_states:
                    existing_states.append(normalized_state)
                    state = State(name=normalized_state)
                    DBSession.add(state)

                if normalized_municipality not in existing_municipalities:
                    existing_municipalities.append(normalized_municipality)
                    municipality = Municipality(name=normalized_municipality,
                                                parent=state)
                    DBSession.add(municipality)

                if row['CNES'] not in existing_clinics:
                    # import ipdb; ipdb.set_trace()
                    existing_clinics.append(row['CNES'])

                    if municipality is None:
                        municipality = Municipality.get(
                            Municipality.name == normalized_municipality)

                    clinic = Clinic(name=row['facility_name'],
                                    code=row['CNES'],
                                    municipality=municipality)
                    DBSession.add(clinic)
