"""
myplatform - Glue code for a unified work environment.

*Under Construction* See Plans.txt (in the parent directory) to see what is going on.

Note: importing this file triggers configuration loading. If this blows up, just importing the module
causes Python to throw up all over you. I may make this behaviour more graceful, but for now, I assume that
users are Python programmers who can figure out what went wrong from the error messages.

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

import os.path
# As a convenience, use the "logging.info" function as log.
from logging import info as log
from myplatform.fetch_base import fetch
import myplatform.configuration


PlatformConfiguration = myplatform.configuration.load_platform_configuration()
import myplatform.utils as utils


LogInfo = utils.PlatformLogger()
# By default, go into the "logs" directory below this file.
if PlatformConfiguration['Logging']['LogDirectory'] == 'DEFAULT':
    LogInfo.LogDirectory = os.path.join(os.path.dirname(__file__), 'logs')
else:
    LogInfo.LogDirectory = PlatformConfiguration['Logging']['LogDirectory']


def start_log(fname=None):
    global LogInfo
    LogInfo.StartLog(fname)