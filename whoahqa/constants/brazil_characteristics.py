from whoahqa.constants.base_characteristics import *  # noqa

# filter CHARACTERISTICS to remove CHARACTERISTIC 4

CHARACTERISTICS = filter(
    lambda x: x[0] not in [FOUR], CHARACTERISTICS)

KEY_INDICATORS = [
    (EQUITABLE, (ONE, TWO, THREE)),
    (ACCESSIBLE, (FIVE, SIX, SEVEN, EIGHT)),
    (ACCEPTABLE, (NINE, TEN, ELEVEN, TWELVE, THIRTEEN, FOURTEEN,
                  FIFTEEN)),
    (APPROPRIATE, (SIXTEEN, )),
    (EFFECTIVE, (SEVENTEEN, EIGHTEEN, NINETEEN, TWENTY))
]

# Characteristic 4 has been removed since health care in brazil is free
# Characteristic 17 has also been removed.
CHARACTERISTIC_MAPPING = {
    ONE: {
        'characteristic_one/ch1_score': [ADOLESCENT_CLIENT,
                                         HEALTH_CARE_PROVIDER,
                                         HEALTH_FACILITY_MANAGER,
                                         ADOLESCENT_IN_COMMUNITY]},
    TWO: {
        'characteristic_two/ch2_score': [ADOLESCENT_CLIENT,
                                         HEALTH_CARE_PROVIDER,
                                         ADOLESCENT_IN_COMMUNITY]},
    THREE: {
        'characteristic_three/ch3_score': [ADOLESCENT_CLIENT,
                                           SUPPORT_STAFF,
                                           ADOLESCENT_IN_COMMUNITY]},
    FIVE: {
        'characteristic_five/ch5_score': [ADOLESCENT_CLIENT,
                                          HEALTH_FACILITY_MANAGER,
                                          ADOLESCENT_IN_COMMUNITY]},
    SIX: {
        'characteristic_six/ch6_score': [ADOLESCENT_CLIENT,
                                         ADOLESCENT_IN_COMMUNITY]},
    SEVEN: {
        'characteristic_seven/ch7_score': [ADOLESCENT_CLIENT,
                                           HEALTH_CARE_PROVIDER,
                                           COMMUNITY_MEMBER,
                                           ADOLESCENT_IN_COMMUNITY]},
    EIGHT: {
        'characteristic_eight/ch8_score': [ADOLESCENT_CLIENT,
                                           HEALTH_FACILITY_MANAGER,
                                           OUTREACH_WORKER,
                                           ADOLESCENT_IN_COMMUNITY]},
    NINE: {
        'characteristic_nine/ch9_score': [ADOLESCENT_CLIENT,
                                          HEALTH_CARE_PROVIDER,
                                          HEALTH_FACILITY_MANAGER,
                                          OBSERVATION_GUIDE]},
    TEN: {
        'characteristic_ten/ch10_score': [ADOLESCENT_CLIENT,
                                          HEALTH_CARE_PROVIDER,
                                          HEALTH_FACILITY_MANAGER,
                                          OBSERVATION_GUIDE]},
    ELEVEN: {
        'characteristic_eleven/ch11_score': [ADOLESCENT_CLIENT,
                                             OBSERVATION_GUIDE]},
    TWELVE: {
        'characteristic_twelve/ch12_score': [ADOLESCENT_CLIENT,
                                             HEALTH_CARE_PROVIDER,
                                             SUPPORT_STAFF,
                                             OBSERVATION_GUIDE]},
    THIRTEEN: {
        'characteristic_thirteen/ch13_score': [ADOLESCENT_CLIENT,
                                               OBSERVATION_GUIDE]},
    FOURTEEN: {
        'characteristic_fourteen/ch14_score': [ADOLESCENT_CLIENT,
                                               HEALTH_FACILITY_MANAGER,
                                               OBSERVATION_GUIDE]},
    FIFTEEN: {
        'characteristic_fifteen/ch15_score': [ADOLESCENT_CLIENT,
                                              HEALTH_FACILITY_MANAGER]},
    SIXTEEN: {
        'characteristic_sixteen/ch16_score': [ADOLESCENT_CLIENT,
                                              HEALTH_CARE_PROVIDER,
                                              HEALTH_FACILITY_MANAGER]},
    SEVENTEEN: {
        'characteristic_seventeen/ch17_score': [ADOLESCENT_CLIENT,
                                                HEALTH_CARE_PROVIDER,
                                                HEALTH_FACILITY_MANAGER]},
    EIGHTEEN: {
        'characteristic_eighteen/ch18_score': [HEALTH_CARE_PROVIDER,
                                               HEALTH_FACILITY_MANAGER,
                                               OBSERVATION_GUIDE]},
    NINETEEN: {
        'characteristic_nineteen/ch19_score': [ADOLESCENT_CLIENT,
                                               HEALTH_CARE_PROVIDER]},
    TWENTY: {
        'characteristic_twenty/ch20_score': [ADOLESCENT_CLIENT,
                                             HEALTH_CARE_PROVIDER,
                                             HEALTH_FACILITY_MANAGER,
                                             OBSERVATION_GUIDE]}
}

QUESTION_COUNT = {
    ONE: {
        ADOLESCENT_CLIENT: 2,
        HEALTH_CARE_PROVIDER: 1,
        HEALTH_FACILITY_MANAGER: 1,
        ADOLESCENT_IN_COMMUNITY: 1},
    TWO: {
        ADOLESCENT_CLIENT: 2,
        HEALTH_CARE_PROVIDER: 1,
        ADOLESCENT_IN_COMMUNITY: 1},
    THREE: {
        ADOLESCENT_CLIENT: 4,
        SUPPORT_STAFF: 1,
        ADOLESCENT_IN_COMMUNITY: 1},
    FIVE: {
        ADOLESCENT_CLIENT: 1,
        HEALTH_FACILITY_MANAGER: 1,
        ADOLESCENT_IN_COMMUNITY: 1},
    SIX: {
        ADOLESCENT_CLIENT: 1,
        ADOLESCENT_IN_COMMUNITY: 1},
    SEVEN: {
        ADOLESCENT_CLIENT: 3,
        HEALTH_CARE_PROVIDER: 1,
        COMMUNITY_MEMBER: 4,
        ADOLESCENT_IN_COMMUNITY: 3},
    EIGHT: {
        ADOLESCENT_CLIENT: 1,
        HEALTH_FACILITY_MANAGER: 1,
        OUTREACH_WORKER: 1,
        ADOLESCENT_IN_COMMUNITY: 2},
    NINE: {
        ADOLESCENT_CLIENT: 5,
        HEALTH_CARE_PROVIDER: 1,
        HEALTH_FACILITY_MANAGER: 1,
        OBSERVATION_GUIDE: 1},
    TEN: {
        ADOLESCENT_CLIENT: 4,
        HEALTH_CARE_PROVIDER: 2,
        HEALTH_FACILITY_MANAGER: 1,
        OBSERVATION_GUIDE: 3},
    ELEVEN: {
        ADOLESCENT_CLIENT: 4,
        OBSERVATION_GUIDE: 4},
    TWELVE: {
        ADOLESCENT_CLIENT: 3,
        HEALTH_CARE_PROVIDER: 2,
        SUPPORT_STAFF: 2,
        OBSERVATION_GUIDE: 1},
    THIRTEEN: {
        ADOLESCENT_CLIENT: 6,
        OBSERVATION_GUIDE: 9},
    FOURTEEN: {
        ADOLESCENT_CLIENT: 6,
        HEALTH_FACILITY_MANAGER: 2,
        OBSERVATION_GUIDE: 2},
    FIFTEEN: {
        ADOLESCENT_CLIENT: 2,
        HEALTH_FACILITY_MANAGER: 2},
    SIXTEEN: {
        ADOLESCENT_CLIENT: 2,
        HEALTH_CARE_PROVIDER: 12,
        HEALTH_FACILITY_MANAGER: 12},
    SEVENTEEN: {
        ADOLESCENT_CLIENT: 6,
        HEALTH_CARE_PROVIDER: 14,
        HEALTH_FACILITY_MANAGER: 13},
    EIGHTEEN: {
        HEALTH_CARE_PROVIDER: 11,
        HEALTH_FACILITY_MANAGER: 11,
        OBSERVATION_GUIDE: 11},
    NINETEEN: {
        ADOLESCENT_CLIENT: 2,
        HEALTH_CARE_PROVIDER: 2},
    TWENTY: {
        ADOLESCENT_CLIENT: 1,
        HEALTH_CARE_PROVIDER: 4,
        HEALTH_FACILITY_MANAGER: 3,
        OBSERVATION_GUIDE: 3}
}

CLINIC_IDENTIFIER = 'facility_info/facility_cnes'
CHARACTERISTIC = 'facility_info/HS_char'
XFORM_ID = '_xform_id_string'
USER_ID = 'user_id'
CLINIC_NAME = 'facility_info/facility_name'
PERIOD_IDENTIFIER = 'facility_info/reporting_period'

MUNICIPALITY_IDENTIFIER = 'facility_info/municipality'
STATE_IDENTIFIER = 'facility_info/state'

AVAILABLE_LANGUAGES = {
    'en': "English",
    'pt': "Portuguese"}

INVALID_CHARACTERISTICS_FLAGS = {
    ONE: 'characteristic_one/ch1_invalid',
    TWO: 'characteristic_two/ch2_invalid',
    THREE: 'characteristic_three/ch3_invalid',
    FIVE: 'characteristic_five/ch5_invalid',
    SIX: 'characteristic_six/ch6_invalid',
    SEVEN: 'characteristic_seven/ch7_invalid',
    EIGHT: 'characteristic_eight/ch8_invalid',
    NINE: 'characteristic_nine/ch9_invalid',
    TEN: 'characteristic_ten/ch10_invalid',
    ELEVEN: 'characteristic_eleven/ch11_invalid',
    TWELVE: 'characteristic_twelve/ch12_invalid',
    THIRTEEN: 'characteristic_thirteen/ch13_invalid',
    FOURTEEN: 'characteristic_fourteen/ch14_invalid',
    FIFTEEN: 'characteristic_fifteen/ch15_invalid',
    SIXTEEN: 'characteristic_sixteen/ch16_invalid',
    EIGHTEEN: 'characteristic_eighteen/ch18_invalid',
    NINETEEN: 'characteristic_nineteen/ch19_invalid',
    TWENTY: 'characteristic_twenty/ch20_invalid'
}
