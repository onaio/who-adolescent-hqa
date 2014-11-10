from whoahqa.constants.base_characteristics import *  # noqa

# filter CHARACTERISTICS to remove CHARACTERISTIC 4

CHARACTERISTICS = filter(lambda x: x[0] is not FOUR, CHARACTERISTICS)

KEY_INDICATORS = [
    (EQUITABLE, (ONE, TWO, THREE)),
    (ACCESSIBLE, (FIVE, SIX, SEVEN, EIGHT)),
    (ACCEPTABLE, (NINE, TEN, ELEVEN, TWELVE, THIRTEEN, FOURTEEN,
                  FIFTEEN)),
    (APPROPRIATE, (SIXTEEN, )),
    (EFFECTIVE, (SEVENTEEN, EIGHTEEN, NINETEEN, TWENTY))
]

CHARACTERISTIC_MAPPING[NINE][ADOLESCENT_CLIENT].update(
    {'characteristic_nine/ch9_q5'})

CHARACTERISTIC_MAPPING[TWELVE][ADOLESCENT_CLIENT] = {
    'characteristic_twelve/ch12_q1',
    'characteristic_twelve/ch12_q2_yes',
    'characteristic_twelve/ch12_q2_yes2'
}

CHARACTERISTIC_MAPPING[FOURTEEN][ADOLESCENT_CLIENT] = {
    'characteristic_twelve/ch14_q1',
    'characteristic_twelve/ch14_q1_Ptg',
    'characteristic_twelve/ch14_q1_yes',
    'characteristic_twelve/ch14_q1_yes2',
    'characteristic_twelve/ch14_q1_yes3',
    'characteristic_twelve/ch14_q1_yes5_Ptg'
}

CHARACTERISTIC_MAPPING[SIXTEEN][HEALTH_CARE_PROVIDER] = {
    'characteristic_sixteen/ch16_q1',
    'characteristic_sixteen/ch16_q2',
    'characteristic_sixteen/ch16_q3',
    'characteristic_sixteen/ch16_q4',
    'characteristic_sixteen/ch16_q5',
    'characteristic_sixteen/ch16_q6',
    'characteristic_sixteen/ch16_q9',
    'characteristic_sixteen/ch16_q10',
    'characteristic_sixteen/ch16_q11',
    'characteristic_sixteen/ch16_q12',
    'characteristic_sixteen/ch16_q13',
    'characteristic_sixteen/ch16_q14'
}

CHARACTERISTIC_MAPPING[SEVENTEEN][HEALTH_CARE_PROVIDER] = {
    'characteristic_seventeen/ch17_q1',
    'characteristic_seventeen/ch17_q2',
    'characteristic_seventeen/ch17_q3',
    'characteristic_seventeen/ch17_q4',
    'characteristic_seventeen/ch17_q5',
    'characteristic_seventeen/ch17_q6',
    'characteristic_seventeen/ch17_q9',
    'characteristic_seventeen/ch17_q10',
    'characteristic_seventeen/ch17_q11',
    'characteristic_seventeen/ch17_q12',
    'characteristic_seventeen/ch17_q13',
    'characteristic_seventeen/ch17_q14',
    'characteristic_seventeen/ch17_q15'
}

CHARACTERISTIC_MAPPING[EIGHTEEN][HEALTH_CARE_PROVIDER] = {
    'characteristic_eighteen/ch18_q1',
    'characteristic_eighteen/ch18_q2',
    'characteristic_eighteen/ch18_q3',
    'characteristic_eighteen/ch18_q4',
    'characteristic_eighteen/ch18_q5',
    'characteristic_eighteen/ch18_q6',
    'characteristic_eighteen/ch18_q9',
    'characteristic_eighteen/ch18_q10',
    'characteristic_eighteen/ch18_q11',
    'characteristic_eighteen/ch18_q12',
    'characteristic_eighteen/ch18_q13'
}
