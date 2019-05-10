"""
Utility functions for testing.

In particular, functions used to control skipping functions and modules will go in here.


"""
import os
import unittest

import econ_platform_core
import econ_platform_core.configuration

# Need this setting if we want to register actions, which we do when unit testing.
econ_platform_core.utils.PlatformEntity._IgnoreRegisterActions = False

def skip_this_extension_module():
    """
    Call this function at the very top of modules that import extensions that import non-standard modules
    (other than pandas). This way we skip the module before we hit imports that will fail.

    (Developers of extensions could protect imports, but having to protect every import would be too painful.)

    :return:
    """
    # TODO: Insert conditional logic here
    raise unittest.SkipTest('this module is skipped because it is an extension module')

def use_test_configuration():
    """
    Force the test config file onto the econ_platform_core.PlatformConfiguration
    :return:
    """
    obj = econ_platform_core.configuration.ConfigParserWrapper()
    # Outside the core, so need to look at relative to this file.
    fpath = os.path.join(os.path.dirname(__file__), 'config_testing.txt')
    obj.Load((fpath,), display_steps=False)

