
import unittest
import os

import econ_platform_core
import econ_platform_core.utils as utils


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



class test_parse_config_directory(unittest.TestCase):
    package_dir = os.path.dirname(econ_platform_core.__file__)
    """
    Note: These tests will fail if someone relocates utils.py, which is probably what we want to happen.
    """
    def test_custom(self):
        self.assertEqual('foo', utils.parse_config_path('foo'))

    def test_case_sensitive(self):
        self.assertEqual('{base}', utils.parse_config_path('{base}'))

    def test_without_sep(self):
        self.assertEqual(test_parse_config_directory.package_dir, utils.parse_config_path('{BASE}'))

    def test_sep1(self):
        self.assertEqual(os.path.join(test_parse_config_directory.package_dir, 'foo'),
                         utils.parse_config_path('{BASE}\\foo'))

    def test_sep2(self):
        self.assertEqual(os.path.join(test_parse_config_directory.package_dir, 'foo'),
                         utils.parse_config_path('{BASE}/foo'))




