"""
Utility functions for testing.

In particular, functions used to control skipping functions and modules will go in here.


"""

import unittest

def skip_this_extension_module():
    """
    Call this function at the very top of modules that import extensions that import non-standard modules
    (other than pandas). This way we skip the module before we hit imports that will fail.

    (Developers of extensions could protect imports, but having to protect every import would be too painful.)

    :return:
    """
    # TODO: Insert conditional logic here
    raise unittest.SkipTest('this module is skipped because it is an extension module')
