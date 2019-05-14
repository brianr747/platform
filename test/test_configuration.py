
import unittest
import os

import loc_utils
import econ_platform_core
import econ_platform_core.configuration as configuration

# Need this line if we want to look at action.
econ_platform_core.utils.PlatformEntity._IgnoreRegisterActions = False

class ConfigTester(unittest.TestCase):
    def setUp(self) -> None:
        loc_utils.use_test_configuration()


    def test_load_nofile(self):
        obj = configuration.ConfigParserWrapper()
        obj.Load(('THIS_BETTER_NOT_BE_A_FILE',))
        self.assertTrue(obj._HasAction('CONFIG:NOTFILE'))

    def test_load_file_and_print_configuration_at_same_time(self):
        obj = econ_platform_core.configuration.ConfigParserWrapper()
        # Assumes that loc_utils is in the same directory as config_testing.txt, which it has to be for
        # the funtion to work.
        self.assertFalse(obj.LoadedAny)
        fpath = os.path.join(os.path.dirname(loc_utils.__file__), 'config_testing.txt')
        # Just in case something else sneaks in...
        obj._ClearActions()
        obj.Load((fpath,), display_steps=False)
        self.assertTrue(obj.LoadedAny)
        self.assertTrue(obj._HasAction(action_class='CONFIG:LOAD', msg_substring='config_testing'))
        msg = configuration.print_configuration(obj, return_string=True)
        self.assertTrue('api_key = ****' in msg)

    def test_load_platform_config(self):
        # Just check that the main files were loaded. Override the environment variable.
        os.environ['PLATFORM_USER_CONFIG'] = "SNERT!"
        obj = configuration.load_platform_configuration(display_steps=False)
        # Since we cannot be sure the files exist, just see whether they appear in a message
        self.assertTrue(obj._HasAction(msg_substring='config_default'))
        self.assertTrue(obj._HasAction(msg_substring='config.txt'))
        self.assertTrue(obj._HasAction(action_class='CONFIG:NOTFILE', msg_substring='SNERT'))

    def test_load_platform_config_2(self):
        # Just check that the main files were loaded. Override the environment variable.
        os.environ['PLATFORM_USER_CONFIG'] = os.path.join(os.path.dirname(loc_utils.__file__), 'config_testing.txt')
        obj = configuration.load_platform_configuration(display_steps=False)
        # Since we cannot be sure the files exist, just see whether they appear in a message
        self.assertTrue(obj._HasAction(msg_substring='config_default'))
        self.assertTrue(obj._HasAction(msg_substring='config.txt'))
        self.assertTrue(obj._HasAction(action_class='CONFIG:LOAD', msg_substring='config_testing.txt'))

    def test_get(self):
        config = configuration.ConfigParserWrapper()
        config.Load([os.path.join(os.path.dirname(__file__), 'config_testing.txt')],
                    display_steps=False)
        self.assertEqual('ExpectedAnswer', config['Options']['ForUnitTest'])







