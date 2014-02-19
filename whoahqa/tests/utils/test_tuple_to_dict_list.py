import unittest

from whoahqa.utils import tuple_to_dict_list


class TestUtils(unittest.TestCase):
    def test_tuple_to_dict_list_creates_dict_from_list_of_tuples(self):
        result = tuple_to_dict_list(
            ("name", "age"),
            [("Billy", 12), ("Bob", 15)])
        self.assertEqual(result, [
            {"name": "Billy", "age": 12},
            {"name": "Bob", "age": 15}
        ])
