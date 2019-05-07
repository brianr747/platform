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
import datetime


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


def entry_lookup(target, row, case_sensitive=True):
    """
    Return the index of a specified target value in a list.
    Throws a KeyError if no match
    :param target: str
    :param row: list
    :param case_sensitive: bool
    :return: int
    """
    if case_sensitive:
        for i in range(0, len(row)):
            if row[i] == target:
                return i
        raise KeyError('{0} not found'.format(target))
    else:
        target = target.lower()
        for i in range(0, len(row)):
            if row[i].lower() == target:
                return i
        raise KeyError('{0} not found'.format(target))


def remove_non_ascii(x):
    """
    Assumes utf-8
    Taken from https://stackoverflow.com/questions/1342000/how-to-make-the-python-interpreter-correctly-handle-non-ascii-characters-in-stri
    :param x:
    :return:
    """
    return "".join(i for i in x if ord(i) < 128)


# Date alignment functions.
def align_by_month(year, month, freq='M'):
    """
    How are calendar dates aligned versus low frequency (monthly, quarterly, annual)...

    By default, first of month convention.

    You can pass year/month as strings; forced to int

    :param year: int
    :param month: int
    :param freq: str
    :return: datetime.date
    """
    freq = freq.upper()
    if freq == 'M':
        return datetime.date(int(year), int(month), 1)
    else:
        raise NotImplementedError('align_by_month() unsupported frequency: {0}'.format(freq))


def iso_string_to_date(d):
    """
    Convert an ISO string date to a datetime.date
    :param d: str
    :return: datetime.date
    """
    return datetime.date(int(d[0:4]), int(d[5:7]), int(d[8:10]))


def coerce_date_to_string(d):
    """
    Force a datetime-like object to an ISO date format string yyyy-mm-dd.

    Not too highly recommended, but used by SQLite, which uses strings for date.

    If there are no year, month, day members, just force to a string. (For things like integer time axes from
    models.)

    :param d: datetime.date
    :return: str
    """
    try:
        return '{0}-{1:02}-{2:02}'.format(d.year, d.month, d.day)
    except:
        # Tough luck
        return str(d)