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



def load_platform_configuration(display_steps=True):
    """
    Goes through the configuration file loading protocol
    :return: configparser.ConfigParser
    """
    config = configparser.ConfigParser()
    code_directory = os.path.dirname(__file__)
    # The default file should always exist...
    if display_steps:
        print('Loading default config:', os.path.join(code_directory, 'config_default.txt'))
    config.read(os.path.join(code_directory, 'config_default.txt'))
    if os.path.exists(os.path.join(code_directory, 'config.txt')):
        if display_steps:
            print('Loading user config:', os.path.join(code_directory, 'config.txt'))
        config.read(os.path.join(code_directory, 'config.txt'))
    # Did the user point to another file?
    # Hey, this is fun!
    act_file = config['ActualConfigFile']['FileName']
    if os.path.exists(act_file):
        if display_steps:
            print('Loading ActualLogFile', act_file)
        config.read(act_file)
    return config


def print_configuration(config):
    for sec in config.sections():
        print('[{0}]'.format(sec))
        for k in config[sec]:
            print(k, '=', config[sec][k])


def main():
    """
    Function for manual testing. Does not make sense to unit test this...
    :return: None
    """
    print('Configuration information')
    obj = load_platform_configuration()
    print_configuration(obj)




if __name__ == '__main__':
    main()