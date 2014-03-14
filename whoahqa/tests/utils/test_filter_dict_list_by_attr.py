import unittest

from whoahqa.utils import filter_dict_list_by_attr


class TestFilterOutActiveCharacteristics(unittest.TestCase):
    ids = ['one', 'two', 'three']
    characteristics = [
        {'name': "Characteristic 1", 'id': 'one'},
        {'name': "Characteristic 1", 'id': 'two'},
        {'name': "Characteristic 1", 'id': 'four'},
        {'name': "Characteristic 1", 'id': 'five'}
    ]

    def test_filters_out_items_in_specified_ids(self):
        filtered_characteristics = filter_dict_list_by_attr(
            self.ids, self.characteristics, 'id')
        self.assertEqual(
            [c['id'] for c in filtered_characteristics], ['one', 'two'])

    def test_filters_out_items_in_specified_ids_with_invert(self):
        filtered_characteristics = filter_dict_list_by_attr(
            self.ids, self.characteristics, 'id', invert=True)
        self.assertEqual(
            [c['id'] for c in filtered_characteristics], ['four', 'five'])
