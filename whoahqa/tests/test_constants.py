import operator
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

    def test_get_score_classification_returns_great_for_80_or_greater(self):
        classification = constants.get_score_classification(80)
        self.assertEqual(classification, constants.GREAT)

    def test_get_score_classification_returns_good_for_60_or_greater(self):
        classification = constants.get_score_classification(60)
        self.assertEqual(classification, constants.GOOD)

    def test_get_score_classification_returns_bad_for_59_or_below(self):
        classification = constants.get_score_classification(59)
        self.assertEqual(classification, constants.BAD)

    def test_get_score_classification_raises_value_error_if_bad_def(self):
        # Bad score ranges
        bad_score_range_limits = (
            (operator.ge, 80, constants.GREAT),
        )
        self.assertRaises(
            ValueError,
            constants.get_score_classification,
            79,
            bad_score_range_limits)
