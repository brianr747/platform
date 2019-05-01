
import unittest
import myplatform.utils as utils


class test_functions(unittest.TestCase):
    def test_convert_ticker(self):
        # This is so obvious that there is no need to break into multiple tests.
        self.assertEqual(utils.convert_ticker_to_variable('abc'), 'abc')
        self.assertEqual(utils.convert_ticker_to_variable('ab$c'), 'ab_c')
        self.assertEqual(utils.convert_ticker_to_variable('ab_c'), 'ab_c')
        self.assertEqual(utils.convert_ticker_to_variable('a.b.c'), 'a_b_c')
        self.assertEqual(utils.convert_ticker_to_variable('1abc'), '_1abc')
        with self.assertRaises(ValueError):
            utils.convert_ticker_to_variable('')

    def test_split_ticker(self):
        self.assertEqual(utils.split_ticker_information('D@ticker'), ('D', 'ticker'))

