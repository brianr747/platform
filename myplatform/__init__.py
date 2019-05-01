"""
myplatform - Glue code for a unified work environment.

*Under Construction*
"""

import os.path
from logging import info as log

print('__init__')
import myplatform.utils as utils

LogInfo = utils.PlatformLogger()
# By default, go into the "logs" directory below this file.
LogInfo.LogDirectory = os.path.join(os.path.dirname(__file__), 'logs')

def start_log(fname=None):
    global LogInfo
    LogInfo.StartLog(fname)