"""
Run the coverage of unit tests - and not end-to-end tests - only.

Although the real coverage includes end-to-end tests, we should know how much is
being done by granular unit tests.


"""

import run_end_to_end_coverage


if __name__ == '__main__':
    run_end_to_end_coverage.main(run_end_to_end=False)