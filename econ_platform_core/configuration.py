"""
configuration.py

Manage platform settings, built on top of configparser.

Designed to allow users to allow the package to "work out of the box" with a text database,
but keep sensitive information (API keys,  database access, etc.) outside of the repository directory structure.

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

import configparser
import os

import econ_platform_core
import econ_platform_core.utils


class ConfigParserWrapper(econ_platform_core.utils.PlatformEntity):
    """
    A wrapper class for the platform configuration loading. All the real work is done by ConfigParser; but
    we need to track that the correct sequence of files is opened.

    This is way over-designed, but I need to be able to control config file parsing closely if we want unit tests
    to work (and want to cover these lines).
    """
    def __init__(self):
        super().__init__()
        self.ConfigParser = configparser.ConfigParser()

    def Load(self, file_list, display_steps=False):
        """
        Load a list of config files. Only work done here:
        (1) Map file paths to the repository directory.
        (2) Unit test support by logging actions.

        :param file_list:
        :param display_steps:
        :return:
        """
        for fname in file_list:
            fname = econ_platform_core.utils.parse_config_path(fname)
            if os.path.exists(fname):
                self._RegisterAction('CONFIG:LOAD', fname)
                if display_steps: # pragma: nocover
                    print('Loading config file: ' + fname)
                self.ConfigParser.read(fname)
            else:
                self._RegisterAction('CONFIG:NOTFILE', fname)
        return self.ConfigParser


def load_platform_configuration(display_steps=True, return_wrapper=False):
    """
    Goes through the configuration file loading protocol
    :return: configparser.ConfigParser
    """
    obj = ConfigParserWrapper()
    # NOTE: Do not worry about the file separators below! They will be fixed by
    # parse_config_path()
    config = obj.Load(('{CORE}/config_default.txt', '{CORE}/config.txt'), display_steps)
    env_variable_name = config['Options']['UserConfigEnvironmentVariableName']
    user_config_file = os.getenv(env_variable_name)
    if user_config_file is not None:
        obj.Load((user_config_file,), display_steps)
    if return_wrapper:
        return obj
    else: # pragma: nocover
        return obj.ConfigParser

def print_configuration(config=None, return_string=False):
    """
    Dump configuration information on the console.
    :param config: configparser.ConfigParser
    :param return_string: bool
    :return:
    """
    if config is None: # pragma: nocover Probably a bad idea to test this...
        config = econ_platform_core.PlatformConfiguration
    msg = ''
    for sec in config.sections():
        msg += '[{0}]\n'.format(sec)
        for k in config[sec]:
            if k.lower() in ('api_key', 'password'):
                msg += '{0} = {1}\n'.format(k, '*********')
            else:
                msg += '{0} = {1}\n'.format(k, config[sec][k])
    if return_string:
        return msg
    print(msg)  # pragma: nocover


def main(): # pragma: nocover
    """
    Function for manual testing. Does not make sense to unit test this...
    :return: None
    """
    print('Configuration information')
    obj = load_platform_configuration()
    print_configuration(obj)


if __name__ == '__main__':  # pragma: nocover
    main()