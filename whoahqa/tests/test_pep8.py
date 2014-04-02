import unittest

from subprocess import call


class TestPEP8(unittest.TestCase):
    def _test_flake8(self):
        result = call(['flake8', 'whoahqa'])
        self.assertEqual(result, 0, "Code is not flake8.")