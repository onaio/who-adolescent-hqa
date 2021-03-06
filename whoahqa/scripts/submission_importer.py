import os
import sys
import transaction
import requests
import itertools


from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from whoahqa.constants import characteristics as constants
from whoahqa.models import (
    Base,
    DBSession,
    Submission)

FORM_MAP = {
    'adolescent_client_V2': 51328,
    'health_care_provider_V2': 51345,
    'support_staff_V2': 51366,
    'health_facility_manager_V2': 51355,
    'outreach_worker_V2': 51373,
    'community_member_V2': 51334,
    'adolescent_in_community_V2': 51330,
    'observation_guide_V2': 51357,
    'adolescent_client_V3': 273344,
    'health_care_provider_V3': 273507,
    'support_staff_V3': 273514,
    'health_facility_manager_V3': 273498,
    'outreach_worker_V3': 273484,
    'community_member_V3': 273500,
    'adolescent_in_community_V3': 273314,
    'observation_guide_V3': 273519,
}


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <form_id_string>\n'
          '(example: "%s development.ini adolescent_client_V3")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 3:
        usage(argv)

    config_uri = argv[1]
    form_id = argv[2]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    client_tool_list = [key for key, _ in itertools.chain(
        constants.CLIENT_TOOLS, constants.CLIENT_TOOLS_V2)]

    if form_id in client_tool_list:
        import_submissions_for(form_id)


def fetch_ona_url(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception("Server responded with %s" % response.status_code)

    raw_data = response.json()

    return raw_data


def fetch_data(form_id):
    headers = {'Authorization':
               'Token 67781e149ab21afafc6a4cc7062cdd79f8618c69'
               }

    url = 'https://api.ona.io/api/v1/data/{}'.format(form_id)

    return fetch_ona_url(url, headers)


def fetch_tool_submissions(form_id):
    raw_data = fetch_data(FORM_MAP[form_id])
    return raw_data


def import_submissions_for(form_id):
    submissions = fetch_tool_submissions(form_id)

    with transaction.manager:
        for submission in submissions:
            Submission.create_from_json(submission)
