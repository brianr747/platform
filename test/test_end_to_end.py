"""
test_end_to_end.py

Unit tests are meant to run extremely quickly, so that we can almost continuously run them while coding.

However, certain things are slow to test. Unfortunately, we need to run them to get 100% test coverage.

Therefore, if we want to test coverage, we need the concept of end-to-end tests.

Will try to concentrate them in this file, but extensions may need them within their test suites.

The idiom used here: Set the environment variable DontRunEndToEnd to 'T' if you want to skip.

Put this marker above the tests that you want to skip.

@unittest.skipIf(skip_end_to_end=='T', 'Slow test excluded')


"""

import pandas

# For modules to be skipped: always do this before other imports!
import loc_utils
loc_utils.skip_this_extension_module()

import os
import unittest
import datetime
import econ_platform_core
from econ_platform_core.providers.provider_example import get_test_series




def user_function(meta, fn_args):
    if not fn_args == '0':
        raise ValueError('bad argument')
    ser = pandas.Series(data=[0], index=[datetime.date(2000,1,1)])
    ser.name = 'testfn(0)'
    return ser

class dummy_test(unittest.TestCase):
    def test_fetch(self):
        config_wrapper = loc_utils.use_test_configuration()
        econ_platform_core.PlatformConfiguration = config_wrapper
        econ_platform_core.init_package()
        loc_utils.delete_data_file('TEST_TEST1.txt')
        ser = econ_platform_core.fetch('TEST@TEST1', database='TEXT')
        targ = get_test_series('TEST1')
        self.assertTrue(targ.equals(ser))
        self.assertTrue(os.path.exists(os.path.join(os.path.dirname(__file__), 'data', 'TEST_TEST1.txt')))
        # fetch again, will be from file.
        ser = econ_platform_core.fetch('TEST@TEST1', database='TEXT')
        self.assertTrue(targ.equals(ser))

    def test_user_function(self):
        config_wrapper = loc_utils.use_test_configuration()
        econ_platform_core.PlatformConfiguration = config_wrapper
        econ_platform_core.init_package()
        User_provider = econ_platform_core.Providers.UserProvider
        User_provider.FunctionMapper['testfn'] = user_function
        ser = econ_platform_core.fetch('U@testfn(0)', database='TEXT')
        self.assertEqual(ser.values,[0])



