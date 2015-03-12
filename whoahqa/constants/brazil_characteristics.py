from whoahqa.constants.base_characteristics import *  # noqa

# filter CHARACTERISTICS to remove CHARACTERISTIC 4

CHARACTERISTICS = filter(
    lambda x: x[0] not in [FOUR, SEVENTEEN], CHARACTERISTICS)

KEY_INDICATORS = [
    (EQUITABLE, (ONE, TWO, THREE)),
    (ACCESSIBLE, (FIVE, SIX, SEVEN, EIGHT)),
    (ACCEPTABLE, (NINE, TEN, ELEVEN, TWELVE, THIRTEEN, FOURTEEN,
                  FIFTEEN)),
    (APPROPRIATE, (SIXTEEN, )),
    (EFFECTIVE, (EIGHTEEN, NINETEEN, TWENTY))
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
        'characteristic_two/ch3_score': [ADOLESCENT_CLIENT,
                                         SUPPORT_STAFF,
                                         ADOLESCENT_IN_COMMUNITY]},
    FIVE: {
        'characteristic_two/ch5_score': [ADOLESCENT_CLIENT,
                                         HEALTH_FACILITY_MANAGER,
                                         ADOLESCENT_IN_COMMUNITY]},
    SIX: {
        'characteristic_two/ch6_score': [ADOLESCENT_CLIENT,
                                         ADOLESCENT_IN_COMMUNITY]},
    SEVEN: {
        'characteristic_two/ch7_score': [ADOLESCENT_CLIENT,
                                         HEALTH_CARE_PROVIDER,
                                         COMMUNITY_MEMBER,
                                         ADOLESCENT_IN_COMMUNITY]},
    EIGHT: {
        'characteristic_two/ch8_score': [ADOLESCENT_CLIENT,
                                         HEALTH_FACILITY_MANAGER,
                                         OUTREACH_WORKER,
                                         ADOLESCENT_IN_COMMUNITY]},
    NINE: {
        'characteristic_two/ch9_score': [ADOLESCENT_CLIENT,
                                         HEALTH_CARE_PROVIDER,
                                         HEALTH_FACILITY_MANAGER,
                                         OBSERVATION_GUIDE]},
    TEN: {
        'characteristic_two/ch10_score': [ADOLESCENT_CLIENT,
                                          HEALTH_CARE_PROVIDER,
                                          HEALTH_FACILITY_MANAGER,
                                          OBSERVATION_GUIDE]},
    ELEVEN: {
        'characteristic_two/ch11_score': [ADOLESCENT_CLIENT,
                                          OBSERVATION_GUIDE]},
    TWELVE: {
        'characteristic_two/ch12_score': [ADOLESCENT_CLIENT,
                                          HEALTH_CARE_PROVIDER,
                                          SUPPORT_STAFF,
                                          OBSERVATION_GUIDE]},
    THIRTEEN: {
        'characteristic_two/ch13_score': [ADOLESCENT_CLIENT,
                                          OBSERVATION_GUIDE]},
    FOURTEEN: {
        'characteristic_two/ch14_score': [ADOLESCENT_CLIENT,
                                          HEALTH_FACILITY_MANAGER,
                                          OBSERVATION_GUIDE]},
    FIFTEEN: {
        'characteristic_two/ch15_score': [ADOLESCENT_CLIENT,
                                          HEALTH_FACILITY_MANAGER]},
    SIXTEEN: {
        'characteristic_two/ch16_score': [ADOLESCENT_CLIENT,
                                          HEALTH_CARE_PROVIDER,
                                          HEALTH_FACILITY_MANAGER]},
    EIGHTEEN: {
        'characteristic_two/ch18_score': [HEALTH_CARE_PROVIDER,
                                          HEALTH_FACILITY_MANAGER,
                                          OBSERVATION_GUIDE]},
    NINETEEN: {
        'characteristic_two/ch19_score': [ADOLESCENT_CLIENT,
                                          HEALTH_CARE_PROVIDER]},
    TWENTY: {
        'characteristic_two/ch20_score': [ADOLESCENT_CLIENT,
                                          HEALTH_CARE_PROVIDER,
                                          HEALTH_FACILITY_MANAGER,
                                          OBSERVATION_GUIDE]}
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
