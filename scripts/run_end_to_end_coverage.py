"""
run_coverage.py

Run coverage command for those of use who don't have it integrated into IDE (or no IDE!).

No guarantee this works!

Copyright 2019 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
from pathlib import Path
import unittest

try:
    import coverage
except ImportError:
    raise Exception('This script will not work if coverage is not installed; "pip install coverage".')

interpreter = sys.executable

print('Running from', interpreter)

def main(run_end_to_end=True):
    print('Invoking coverage')
    parent = Path(os.path.dirname(__file__)).parent
    test_dir = os.path.join(parent, 'test')
    print('Running in ', test_dir)
    os.chdir(test_dir)
    if run_end_to_end:
        os.environ['RUN_END_TO_END'] = 'T'
    else:
        # Override settings...
        os.environ['RUN_END_TO_END'] = 'F'
    print('Starting')
    cov = coverage.Coverage(omit=["loc_utils.py", '*site-package*', 'test*'])
    cov.start()
    tester = unittest.TestLoader()
    suite = tester.discover('.')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
    cov.stop()
    cov.html_report(directory='htmlcov')


if __name__ == '__main__':
    main()
