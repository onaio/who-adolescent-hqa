import unittest
from datetime import datetime

import colander

from whoahqa.forms.reporting_period import StartEndDateValidator


class TestStartEndValidator(unittest.TestCase):
    def test_passes_if_start_date_lt_end_date(self):
        validator = StartEndDateValidator()
        self.assertIsNone(
            validator.__call__(
                {
                    'start_date': None
                },
                {
                    'start_date': datetime(2014, 3, 13),
                    'end_date': datetime(2015, 3, 13)
                }
            )
        )

    def test_raises_invalid_if_start_date_lte_end_date(self):
        validator = StartEndDateValidator()
        self.assertRaises(
            colander.Invalid,
            validator.__call__,
            {
                'start_date': None
            },
            {
                'start_date': datetime(2014, 3, 1),
                'end_date': datetime(2014, 3, 1)
            }
        )
