import unittest

from datetime import date
from pyramid import testing

from whoahqa.utils import format_date_for_locale


class TestLocaleDate(unittest.TestCase):
    def test_returns_date_string_as_per_request_locale(self):
        request = testing.DummyRequest()
        formatted_date = format_date_for_locale(
            date(2014, 3, 13), "MMM Y", request)
        self.assertEqual(formatted_date, "Mar 2014")
