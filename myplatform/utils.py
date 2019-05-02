"""
utils.py


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

import logging
import sys
import os
import re

class PlatformLogger(object):
    """
    Add a convenient front end to the logging module
    """
    def __init__(self):
        self.LogDirectory = '.'
        self.LogName = 'log.txt'
        self.Format = '%(asctime)s\t%(levelname)s\t%(message)s'
        self.DateFormat = '%Y-%m-%d %H:%M:%S'
        self.FileMode = 'w'

    def StartLog(self, log_name=None):
        if log_name is None:
            log_name = os.path.basename(sys.argv[0])
            pos = log_name.rfind('.')
            if pos > -1:
                log_name = log_name[0:pos]
            log_name = 'log_'+ log_name + '.txt'
        full_name = os.path.join(self.LogDirectory, log_name)
        logging.basicConfig(filename=full_name, filemode=self.FileMode, format=self.Format, datefmt=self.DateFormat,
                            level=logging.DEBUG)


def convert_ticker_to_variable(ticker):
    """
    Convert a ticker to a valid variable name (which passes for a file name).

    Based on answer from Triptych
    https://stackoverflow.com/questions/3303312/how-do-i-convert-a-string-to-a-valid-variable-name-in-python
    I never figured out regular expressions...

    :param ticker: str
    :return: str
    """
    if len(ticker) == 0:
        raise ValueError('Cannot deal with empty tickers')
    try:
        ticker = re.sub('[^0-9a-zA-Z_]', '_', ticker)
    except:
        print('Failure parsing', ticker)
        raise
    # Not sure how to this with re
    if ticker[0].isdigit():
        ticker = '_' + ticker
    return ticker


def split_ticker_information(ticker):
    """
    Split a ticker into a (source_code, source_ticker) pair.

    For now, no error handling...
    :param ticker: str
    :return: tuple
    """
    source_code, source_ticker = ticker.split('@')
    return (source_code, source_ticker)

def get_platform_directory():
    """
    Where is the directory of this package? (Used as default position for files).
    :return: str
    """
    return os.path.dirname(__file__)