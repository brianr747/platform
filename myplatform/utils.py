
print('utils.py')

import logging
import sys
import os

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





