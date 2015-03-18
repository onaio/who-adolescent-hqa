import unittest
from datetime import datetime

import colander

from whoahqa.forms.reporting_period import MonthYearDate


class TestMonthYearDate(unittest.TestCase):
    def test_serialize_converts_date_time_to_string(self):
        month_year = MonthYearDate()
        value = month_year.serialize(None, datetime(2014, 3, 13))
        self.assertEqual(value, "13-03-2014")

    def test_serialize_raises_invalid_if_not_datetime(self):
        month_year = MonthYearDate()
        self.assertRaises(
            colander.Invalid, month_year.serialize, None, "not-a-date")

    def test_deserialize_returns_null_if_null(self):
        month_year = MonthYearDate()
        value = month_year.deserialize(None, colander.null)
        self.assertEqual(value, colander.null)

    def test_deserialize_converts_straing_to_datetime(self):
        month_year = MonthYearDate()
        value = month_year.deserialize(None, "1-03-2014")
        self.assertEqual(value, datetime(2014, 3, 1))

    def test_deserialize_raises_invalid_if_not_basestring(self):
        month_year = MonthYearDate()
        self.assertRaises(
            colander.Invalid, month_year.deserialize, None, 1)

    def test_deserialize_raises_invalid_if_bad_date_string(self):
        month_year = MonthYearDate()
        self.assertRaises(
            colander.Invalid, month_year.deserialize, None, "2014-13")
