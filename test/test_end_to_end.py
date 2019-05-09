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


import os
import unittest

import loc_utils

# Testing the skip functionality
loc_utils.skip_this_extension_module()

skip_end_to_end = os.getenv('DontRunEndToEnd')

class dummy_test(unittest.TestCase):
    def test_fail(self):
        self.assertTrue(False)