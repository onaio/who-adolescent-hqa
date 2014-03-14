import unittest

from whoahqa import constants


class TestConstants(unittest.TestCase):
    def test_characteristic_indicator_mapping(self):
        self.assertDictEqual(
            constants.CHARACTERISTIC_INDICATOR_MAPPING,
            {
                constants.ONE: constants.EQUITABLE,
                constants.TWO: constants.EQUITABLE,
                constants.THREE: constants.EQUITABLE,
                constants.FOUR: constants.ACCESSIBLE,
                constants.FIVE: constants.ACCESSIBLE,
                constants.SIX: constants.ACCESSIBLE,
                constants.SEVEN: constants.ACCESSIBLE,
                constants.EIGHT: constants.ACCESSIBLE,
                constants.NINE: constants.ACCEPTABLE,
                constants.TEN: constants.ACCEPTABLE,
                constants.ELEVEN: constants.ACCEPTABLE,
                constants.TWELVE: constants.ACCEPTABLE,
                constants.THIRTEEN: constants.ACCEPTABLE,
                constants.FOURTEEN: constants.ACCEPTABLE,
                constants.FIFTEEN: constants.ACCEPTABLE,
                constants.SIXTEEN: constants.APPROPRIATE,
                constants.SEVENTEEN: constants.EFFECTIVE,
                constants.EIGHTEEN: constants.EFFECTIVE,
                constants.NINETEEN: constants.EFFECTIVE,
                constants.TWENTY: constants.EFFECTIVE
            })
