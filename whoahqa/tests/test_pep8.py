import unittest

from subprocess import call


class TestPEP8(unittest.TestCase):
    def test_flake8(self):
        result = call(['flake8', 'whoahqa', '--exclude', 'whoahqa/static'])
        self.assertEqual(result, 0, "Code is not flake8.")
