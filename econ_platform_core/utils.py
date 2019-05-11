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


class PlatformEntity(object):
    """
    Base class for objects in the platform. Give an action-logging interface.
    """
    _IgnoreRegisterActions = True
    def __init__(self):
        self._Actions = []

    def _RegisterAction(self, action_class, action_msg, *args):
        """
        Register actions in the object "_Actions" property.

        Used for unit-testing/debugging.

        The *args are parsed via msg.format(args). (We skip the formatting effort if
        we skip registration.)

        Does nothing if PlatformEntity._IgnoreRegisterActions is True (default).

        (This eliminates the performance hit of registration when used in production.)

        :param action_class: str
        :param action_msg: str
        :param args: tuple
        :return:
        """
        if self._IgnoreRegisterActions:
            return
        self._Actions.append((action_class, action_msg.format(args)))

    def _ClearActions(self):
        """
        Clear the action list. (Call ahead of running tests.
        :return:
        """
        self._Actions = []

    def _HasAction(self, action_class=None, msg_substring=None):
        """
        Convenience method for testing.

        Set either action_class or msg_substring.

        Looks for an actions that:

        (1) action_class matches *exactly* the search parameter
        (2) msg_substring appears in the  action message.

        If both are set, both consitions must hold for a single action.

        :param action_class: str
        :param msg_substring: str
        :return: bool
        """
        if action_class is not None and msg_substring is None:
            return action_class in [x[0] for x in self._Actions]
        if action_class is None and msg_substring is not None:
            for x in self._Actions:
                if msg_substring in x[1]:
                    return True
            return False
        if action_class is not None and msg_substring is not None:
            for x in self._Actions:
                if action_class == x[0] and msg_substring in x[1]:
                    return True
            return False
        raise ValueError('Must have at least one non-None input to HasAction()')


class PlatformLogger(PlatformEntity):
    """
    Add a convenient front end to the logging module
    """
    def __init__(self):
        super().__init__()
        self.LogDirectory = ''
        self.LogName = 'log.txt'
        self.Format = '%(asctime)s\t%(levelname)s\t%(message)s'
        self.DateFormat = '%Y-%m-%d %H:%M:%S'
        self.FileMode = 'w'

    def StartLog(self, log_name=None): # pragma: nocover  Pretty brutal effort needed to test this...
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
        raise ValueError('Cannot parse ticker: {0}'.format(ticker))
    # Not sure how to this with re
    if ticker[0].isdigit():
        ticker = '_' + ticker
    return ticker


def split_ticker_information(ticker):
    """
    Split a ticker into a (source_code, source_ticker) pair.
    DEPRECATED: use ticker.py

    For now, no error handling...
    :param ticker: str
    :return: tuple
    """
    # Leave this off for now.
    # logging.warning('split_ticker_information() is deprecated.')
    source_code, source_ticker = ticker.split('@')
    return (source_code, source_ticker)


def parse_config_path(fpath):
    """
    Parse a path in config files.

    (1) If the path does not contain '{CORE}' or '{DATA}', it is a non-default path, so return unchanged.
    (2) If the path contains '{CORE}', it is a default that is going into the platform package
    directory structure. (Why? These are the only directories that we now exist, other than the current
    directory.)

    (a) The term '{CORE}' is replaced with the directory of this file (assumed to be the base of the package.),
    or '{DATA}' with '{CORE}/data'.
    (b) All directory seperators ("/", "\") are replaced with the correct path seperator for the OS.

    :param fpath: str
    :return: str
    """
    if not(('{CORE}' in fpath) or ('{DATA}' in fpath)):
        return fpath
    # Default path; go to work.
    # Make all seperators the same.
    fpath = fpath.replace('\\', '/')
    fpath_s = fpath.split('/')
    new_path = os.path.sep.join(fpath_s)
    new_path = new_path.replace('{DATA}', os.path.join('{CORE}', 'data'))
    new_path = new_path.replace('{CORE}', os.path.dirname(__file__))
    return new_path


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


def remove_non_ascii(x): # pragma: nocover  (No idea how to generate non-ASCII characters..
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


