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
from logging import info as log, info


import myplatform.configuration
from myplatform import utils as utils

try:
    # It would be good to log the loading of configuration information, except that the logging
    # configuration is loaded in this step!
    # Try to load configuration silently...
    PlatformConfiguration = myplatform.configuration.load_platform_configuration(display_steps=False)
except:
    # it failed, so try again, showing the steps...
    myplatform.configuration.load_platform_configuration(display_steps=True)
    raise


# Get the logging information. Users can either programmatically change the LogInfo.LogDirectory or
# use a config file before calling start_log()
LogInfo = utils.PlatformLogger()
# By default, go into the "logs" directory below this file.
if PlatformConfiguration['Logging']['LogDirectory'] == 'DEFAULT':
    LogInfo.LogDirectory = os.path.join(os.path.dirname(__file__), 'logs')
else:
    LogInfo.LogDirectory = PlatformConfiguration['Logging']['LogDirectory']


def start_log(fname=None):
    """
    Call this function if you want a log. By default, the log name is based on the base Python script name
    (sys.argv[0]), and goes into the default directory (LonInfo.LogDirectory).
    :param fname: str
    :return:
    """
    global LogInfo
    LogInfo.StartLog(fname)


class DatabaseManager(object):
    """
    This is the base class for Database Managers.
    """
    def Exists(self, ticker):
        """

        :param ticker: str
        :return: bool
        """
        raise NotImplementedError()

    def Write(self, ser, ticker):
        """

        :param ser: pandas.Series
        :param ticker: str
        :return:
        """
        raise NotImplementedError()


class DatabaseList(object):
    """
    List of all Database managers. Developers can push their own DatabaseManagers into the global object.
    """
    def __init__(self):
        self.DatabaseDict = {}

    def Initialise(self):
        # Need to hide this import until we have finished importing all the class definitions.
        # This is because myplatform.databases.text_database imports this file.
        import myplatform.databases.text_database
        self.DatabaseDict['TEXT'] = myplatform.databases.text_database.TextDatabase()

    def __getitem__(self, item):
        """
        Access method
        :param item: str
        :return: DatabaseManager
        """
        return self.DatabaseDict[item]


Databases = DatabaseList()


def get_provider_code(provider_name):
    """
    Get the provider code associated with the given provider name in the configuration information.

    Case insensitive name matching, provider codes are always upper case.

    If we define two codes as being the same provider, will return one arbitrary choice...

    :param provider_name: str
    :return: str
    """
    # only trick is that the codes are the keys to the configuration section
    code_section = PlatformConfiguration['Providers']
    for k in code_section.keys():
        if provider_name.lower() == code_section[k].lower():
            return k.upper()
    # If we reach this, no match!
    raise KeyError('Provider "{0}" is not in the configuration information'.format(provider_name))

class ProviderWrapper(object):
    """
    Data provider class. Note that we call them "providers" and not "sources" since the source is the
    agency in the real world that calculates the data. The provider and the source can be the same - for example,
    if we get Eurostat data from Eurostat itself. However, we can get Eurostat data from DB.nomics.

    """
    def __init__(self, name='VirtualObject'):
        self.ProviderName = name
        self.ProviderCode = ''
        if not name == 'VirtualObject':
            self.ProviderCode = get_provider_code(name)

    def fetch(self, provider_ticker):
        raise NotImplementedError


class ProviderList(object):
    """
    List of all proviser wrappers. Developers can push their own DatabaseManagers into the global object.
    """
    def __init__(self):
        self.ProviderDict = {}

    def Initialise(self):
        # Need to hide this import until we have finished importing all the class definitions.
        # This is because the provider wrappers probably import this file.
        import myplatform.providers.provider_dbnomics
        obj = myplatform.providers.provider_dbnomics.ProviderDBnomics()
        print(obj.ProviderCode)
        self.ProviderDict[obj.ProviderCode] = obj

    def __getitem__(self, item):
        """
        Access method
        :param item: str
        :return: ProviderWrapper
        """
        return self.ProviderDict[item]

Providers = ProviderList()

def init_package():
    """
    Call to initialise the package, other than configuration file (and logging set up).
    :return:
    """
    Databases.Initialise()
    Providers.Initialise()





def fetch(ticker, database='Default', dropna=True):
    """
    Fetch a series from database; may create series and/or update as needed.

    :param ticker: str
    :param database: str
    :param dropna: bool
    :param always_list: bool
    :return: pandas.Series
    """
    # NOTE: This will get fancier, but don't over-design for now...
    if database=='Default':
        database = 'TEXT'
    if not database=='TEXT':
        raise NotImplementedError('Only the text database supported!')
    database_manager = Databases[database]
    try:
        provider_code, provider_ticker = utils.split_ticker_information(ticker)
    except:
        raise NotImplementedError('We assume that all tickers are of the form {provider{}@{provider_ticker}')
    try:
        provider_manager = Providers[provider_code]
    except:
        raise KeyError('Unknown provider_code: ' + provider_code)

    if database_manager.Exists(ticker):
        # TODO: Handle series updates.
        # Return what is on the database.
        return database_manager.Retrieve(ticker)
    else:
        log('Fetching %s', ticker)
        ser_list = provider_manager.fetch(provider_ticker)
        if dropna:
            ser_list = [x.dropna() for x in ser_list]
        if len(ser_list) > 1:
            raise NotImplementedError('More than one series in a fetch not supported')
        log('Writing %s', ticker)
        for x in ser_list:
            database_manager.Write(x, x.name)
    return ser_list[0]

# If we have problems with initialisation, may need to not execute here - user has to call.
init_package()