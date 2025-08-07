import unittest

class TestGetDictDiff(unittest.TestCase):

    def setUp(self):
        class Dummy:
            def get_dict_diff_based_on_original_value(self, current_value, original_value, key, value, diff_dict, original_dict):
                if (value != original_value.get(key)):
                    diff_dict[key] = value
                    original_dict[key] = original_value.get(key)
                return diff_dict, original_dict

        self.obj = Dummy()

    def test_value_changed(self):
        current_value = {'name': 'Vamsi','loan_status' : 'Success'}
        original_value = {'name': 'Mandala','loan_status' : 'Pending'}
        diff_dict = {} 
        original_dict = {} 
        
        for key,value in 

        diff, original = self.obj.get_dict_diff_based_on_original_value(
            current_value, original_value, 'name', 'Vamsi', diff_dict, original_dict
        )

        self.assertEqual(diff, {'name': 'Vamsi'})
        self.assertEqual(original, {'name': 'Mandala'})

    def test_value_same(self):
        current_value = {'name': 'John'}
        original_value = {'name': 'John'}
        diff_dict = {}
        original_dict = {}

        diff, original = self.obj.get_dict_diff_based_on_original_value(
            current_value, original_value, 'name', 'John', diff_dict, original_dict
        )

        self.assertEqual(diff, {})
        self.assertEqual(original, {})

    def test_key_not_in_original(self):
        current_value = {'age': 25}
        original_value = {}  # 'age' key missing
        diff_dict = {}
        original_dict = {}

        diff, original = self.obj.get_dict_diff_based_on_original_value(
            current_value, original_value, 'age', 25, diff_dict, original_dict
        )

        self.assertEqual(diff, {'age': 25})
        self.assertEqual(original, {'age': None})


if __name__ == '__main__':
    unittest.main()
