from rest_framework.test import APITestCase

class DiffValueAPITestCase(APITestCase):
    def get_dict_diff_based_on_original_value(self, current_value, original_value, key,
            value, diff_dict, original_dict):
        if(isinstance(original_value, list)):
            return value, original_value
        if (value != original_value.get(key)):
                    diff_dict[key] = value
                    original_dict[key] = original_value.get(key)
                    return diff_dict, original_dict
    
    def test_list_to_list(self):
        original_value = ['Pending']
        current_value = ['Success']
        key = "Emi_status"
        value = 'Success'
        diff_dict = {}
        original_dict = {}

        expected = ('Success', ['Pending'])

        result = self.get_dict_diff_based_on_original_value(
            current_value, original_value, key, value, diff_dict, original_dict
        )

        self.assertEqual(result, expected)
        
    def test_dict_to_dict(self):
        original_value = {"Emi_status": "Pending"}
        current_value = {"Emi_status": "Success"}
        key = "Emi_status"
        value = 'Success'
        diff_dict = {}
        original_dict = {}

        expected = {"Emi_status": "Success"}, {"Emi_status": "Pending"}

        result = self.get_dict_diff_based_on_original_value(
            current_value, original_value, key, value, diff_dict, original_dict
        )

        self.assertEqual(result, expected)    
        
        
    def test_list_to_dict(self):
        original_value = ['Pending']
        current_value = {"Emi_status": "Success"}
        key = "Emi_status"
        value = 'Success'
        diff_dict = {}
        original_dict = {}

        expected = ('Success', ['Pending'])

        result = self.get_dict_diff_based_on_original_value(
            current_value, original_value, key, value, diff_dict, original_dict
        )

        self.assertEqual(result, expected)
        
        
    def test_dict_to_list(self):
        original_value = {"Emi_status": "Pending"}
        current_value =  ["Success"]
        key = "Emi_status"
        value = 'Success'
        diff_dict = {}
        original_dict = {}

        expected = {"Emi_status": "Success"}, {"Emi_status": "Pending"}

        result = self.get_dict_diff_based_on_original_value(
            current_value, original_value, key, value, diff_dict, original_dict
        )

        self.assertEqual(result, expected)
            
 
            