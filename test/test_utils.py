
import unittest
import os
import datetime

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

    def test_convert_2_ticker(self):
        self.assertEqual('c_a_t', utils.convert_ticker_to_variable('c$a$t'))

    def test_convert_2_ticker_exception(self):
        with self.assertRaises(ValueError):
            utils.convert_ticker_to_variable(['a'])

    def test_entry_lookup_1(self):
        row = ['a', 'b', 'c']
        self.assertEqual(1, utils.entry_lookup('b', row))

    def test_entry_lookup_2(self):
        row = ['a', 'b', 'c']
        with self.assertRaises(KeyError):
            self.assertEqual(1, utils.entry_lookup('B', row))

    def test_entry_lookup_3(self):
        row = ['a', 'b', 'c']
        self.assertEqual(1, utils.entry_lookup('B', row, case_sensitive=False))

    def test_entry_lookup_4(self):
        row = ['a', 'b', 'c']
        with self.assertRaises(KeyError):
            self.assertEqual(1, utils.entry_lookup('x', row, case_sensitive=False))

    def test_align_by_month(self):
        self.assertEqual(datetime.date(2000, 1, 1), utils.align_by_month(2000, 1, freq='M'))

    def test_align_by_month_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            utils.align_by_month(2000, 1, freq='ZZ')

    def test_ISO_string_to_date(self):
        self.assertEqual(datetime.date(2000, 1, 1), utils.iso_string_to_date('2000-01-01 BLAH BLAH TIME'))

    def test_coerce_date_to_string(self):
        self.assertEqual('2000-01-01', utils.coerce_date_to_string(datetime.date(2000, 1, 1)))

    def test_coerce_numeric_date_to_string(self):
        # Note sure what format 1. will be converted to as a string.
        self.assertEqual(str(1.), utils.coerce_date_to_string(1.))

    def test_param_dict_1(self):
        self.assertEqual('|p=v|', utils.dict_to_param_string({'p': 'v'}))

    def test_param_dict_2(self):
        # Note: keys are in alphabetical order
        self.assertEqual('!a=b_!p_=v_!', utils.dict_to_param_string({'p=': 'v!',
                                                                    'a': 'b='}, delim='!'))

    def test_param_str_to_dict_1(self):
        self.assertDictEqual({'A': 'B'}, utils.param_string_to_dict('|A=B|', delim='|'))

    def test_param_str_to_dict_reverse(self):
        targ = {'A': 'B', 'x': 'y'}
        # Don't specify the delimiters
        param = utils.dict_to_param_string(targ)
        self.assertDictEqual(targ, utils.param_string_to_dict(param))

    def test_archive(self):
        """
        Do all the archive tests in one shot, since order matters.

        :return:
        """
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        archive_dir = os.path.join(data_dir, 'archive')
        if os.path.exists(archive_dir):
            os.rmdir(archive_dir)
        self.assertFalse(os.path.exists(archive_dir))
        fname_1 = os.path.join(data_dir, 'archive_1.txt')
        f = open(fname_1, 'w')
        f.close()
        self.assertTrue(os.path.exists(fname_1))
        utils.archive_file(fname_1, archive_subdir='archive')
        self.assertTrue(os.path.exists(os.path.join(archive_dir, 'archive_1.txt')))
        self.assertFalse(os.path.exists(fname_1))
        # clean up
        os.remove(os.path.join(archive_dir, 'archive_1.txt'))
        os.rmdir(archive_dir)









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
        self.assertEqual(test_parse_config_directory.package_dir, utils.parse_config_path('{CORE}'))

    def test_sep1(self):
        self.assertEqual(os.path.join(test_parse_config_directory.package_dir, 'foo'),
                         utils.parse_config_path('{CORE}\\foo'))

    def test_sep2(self):
        self.assertEqual(os.path.join(test_parse_config_directory.package_dir, 'foo'),
                         utils.parse_config_path('{CORE}/foo'))

    def test_sep3(self):
        self.assertEqual(os.path.join(test_parse_config_directory.package_dir, 'data'),
                         utils.parse_config_path('{DATA}'))


class test_PlatformEntity(unittest.TestCase):
    def setUp(self) -> None:
        utils.PlatformEntity._IgnoreRegisterActions = False

    def test_no_actions(self):
        utils.PlatformEntity._IgnoreRegisterActions = True
        obj = utils.PlatformEntity()
        self.assertEqual([], obj._Actions)
        obj._RegisterAction('A', 'B')
        self.assertEqual([], obj._Actions)
        # We want to register actions in unit tests; make sure this is reset.
        utils.PlatformEntity._IgnoreRegisterActions = False

    def test_msg_false(self):
        obj = utils.PlatformEntity()
        obj._RegisterAction('', 'x')
        self.assertFalse(obj._HasAction(None, 'Y'))

    def test_both_miss(self):
        obj = utils.PlatformEntity()
        obj._RegisterAction('a', 'b')
        obj._RegisterAction('c', 'd')
        self.assertFalse(obj._HasAction('b', 'a'))

    def test_no_test(self):
        obj = utils.PlatformEntity()
        with self.assertRaises(ValueError):
            obj._HasAction()

    def test_find_action(self):
        obj = utils.PlatformEntity()
        obj._RegisterAction('a', 'b')
        obj._RegisterAction('c', 'd')
        self.assertTrue(obj._HasAction('a', None))

    def test_find_msg(self):
        obj = utils.PlatformEntity()
        obj._RegisterAction('a', 'bbb')
        obj._RegisterAction('c', 'ddd')
        self.assertTrue(obj._HasAction(None, 'bb'))





