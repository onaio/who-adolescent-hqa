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
    'characteristic_nine/ch9_q5')

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
