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
