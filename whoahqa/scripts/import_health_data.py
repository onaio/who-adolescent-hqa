import os
import sys
import csv
import codecs
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

from ..utils import normalizeString


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


class UnicodeDictReader(object):
    def __init__(self, *args, **kw):
        self.encoding = kw.pop('encoding', 'utf-8')
        self.reader = csv.DictReader(*args, **kw)

    def __iter__(self):
        decode = codecs.getdecoder(self.encoding)
        for row in self.reader:
            t = dict((k, decode(row[k])[0]) for k in row)
            yield t


def import_health_data():
    file_name = os.path.relpath('whoahqa/data/New_Locations.csv')
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
                normalized_state = normalizeString(row['State'])
                normalized_municipality = normalizeString(
                    row['Municipality'])

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

                    clinic = Clinic(name=row['Health Facility'],
                                    code=row['CNES'],
                                    municipality=municipality)
                    DBSession.add(clinic)
