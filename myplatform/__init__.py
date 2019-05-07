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
import pandas
import traceback

# As a convenience, use the "logging.info" function as log.
from logging import info as log, info, debug as log_debug, warning as log_warning, error as log_error

try:
    import matplotlib.pyplot as plt
    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()
except ImportError:
    plt = None
    pass

import myplatform.configuration
from myplatform import utils as utils
import myplatform.extensions

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


class SeriesMetaData(object):
    """
    Class that holds series meta data used on the platform.
    """
    def __init__(self):
        # Kind of strange, but does this series yet exist on the database in question?
        self.Exists = False
        self.series_id = -1
        self.series_provider_code = ''
        self.ticker_full = ''
        self.ticker_local = ''
        self.ticker_query = ''
        self.ProviderMetaData = {}

    def __str__(self):
        out = ''
        for name in dir(self):
            if name.startswith('_'):
                continue
            out += '{0}\t{1}\n'.format(name, str(getattr(self, name)))
        return out

class DatabaseManager(object):
    """
    This is the base class for Database Managers.

    Note: Only support full series replacement for now.
    """
    def __init__(self, name='Virtual Object'):
        self.Name = name
        if not name == 'Virtual Object':
            self.Code = PlatformConfiguration['DatabaseList'][name]
        self.ReplaceOnly = True

    def Find(self, ticker):
        """
        Can we find the ticker on the database? Default behaviour is generally adequate.
        :param ticker: str
        :return: SeriesMetaData
        """
        try:
            provider_code, query_ticker = ticker.split('@')
        except:
            return self._FindLocal(ticker)
        meta = SeriesMetaData()
        meta.ticker_local = ''
        meta.ticker_full = ticker
        meta.ticker_query = query_ticker
        meta.series_provider_code  = provider_code
        meta.Exists = self.Exists(ticker)
        # Provider-specific meta data data not supported yet.
        return meta

    def _FindLocal(self, local_ticker):
        """
        Databases that support local tickers should override this method.

        :param local_ticker: SeriesMetaData
        :return:
        """
        raise NotImplementedError('This database does not support local tickers')


    def Exists(self, ticker):
        """

        :param ticker: str
        :return: bool
        """
        raise NotImplementedError()

    def Retrieve(self, series_meta):
        """

        :param series_meta: SeriesMetaData
        :return: pandas.Series
        """
        raise NotImplementedError()

    def GetMeta(self, full_ticker):
        raise NotImplementedError()

    def RetrieveWithMeta(self, full_ticker):
        """
        Retrieve both the meta data and the series. Have a single method in case there is
        an optimisation for the database to do both queries at once.

        Since we normally do not want the meta data at the same time, have the usual workflow to just
        use the Retrieve() interface.

        :param full_ticker: str
        :return: list
        """
        meta = self.GetMeta(full_ticker)
        ser = self.Retrieve(meta)
        return ser, meta


    def Write(self, ser, series_meta, overwrite=True):
        """

        :param ser: pandas.Series
        :param series_meta: SeriesMetaData
        :param overwrite: bool
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
        import myplatform.databases.database_text
        self.AddDatabase(myplatform.databases.database_text.DatabaseText())

    def AddDatabase(self, wrapper):
        """

        :param wrapper: DatabaseManager
        :return:
        """
        self.DatabaseDict[wrapper.Code] = wrapper

    def __getitem__(self, item):
        """
        Access method
        :param item: str
        :return: DatabaseManager
        """
        return self.DatabaseDict[item]

    def TransferSeries(self, full_ticker, source, dest):
        """
        Transfer a series from one database to another.

        Useful for migrations and testing.

        :param full_ticker: str
        :param source: str
        :param dest: str
        :return:
        """
        source_manager = self[source]
        dest_manager = self[dest]
        ser, meta = source_manager.RetrieveWithMeta(full_ticker)
        # The meta information should be the same, except the Exists flag...
        meta.Exists = dest_manager.Exists(full_ticker)
        dest_manager.Write(ser, meta)


Databases = DatabaseList()


class ProviderWrapper(object):
    """
    Data provider class. Note that we call them "providers" and not "sources" since the source is the
    agency in the real world that calculates the data. The provider and the source can be the same - for example,
    if we get Eurostat data from Eurostat itself. However, we can get Eurostat data from DB.nomics.

    """
    Name: str

    def __init__(self, name='VirtualObject'):
        self.Name = name
        self.ProviderCode = ''
        self.IsExternal = True
        if not name == 'VirtualObject':
            self.ProviderCode = PlatformConfiguration['ProviderList'][name]

    def fetch(self, series_meta):
        raise NotImplementedError


class ProviderList(object):
    """
    List of all proviser wrappers. Developers can push their own DatabaseManagers into the global object.
    """
    def __init__(self):
        self.ProviderDict = {}
        self.EchoAccess = PlatformConfiguration['ProviderOptions'].getboolean('echo_access')

    def Initialise(self):
        # Need to hide this import until we have finished importing all the class definitions.
        # This is because the provider wrappers probably import this file.
        import myplatform.providers.provider_user
        self.AddProvider(myplatform.providers.provider_user.ProviderUser())

    def AddProvider(self, obj):
         """
         Add a provider
         :param obj: ProviderWrapper
         :return:
         """
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

class PlatformError(Exception):
    pass

class TickerError(PlatformError):
    pass

class TickerNotFoundError(PlatformError):
    pass

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
    if database.lower()=='default':
        database = PlatformConfiguration["Database"]["Default"]
    database_manager: DatabaseManager = Databases[database]
    series_meta = database_manager.Find(ticker)
    provider_code = series_meta.series_provider_code
    try:
        provider_manager: ProviderWrapper = Providers[provider_code]
    except:
        raise KeyError('Unknown provider_code: ' + provider_code)

    if series_meta.Exists:
        # TODO: Handle series updates.
        # Return what is on the database.
        log_debug('Fetching {0} from {1}'.format(ticker, database_manager.Name))
        return database_manager.Retrieve(series_meta)
    else:
        if provider_manager.IsExternal:
            _hook_fetch_external(provider_manager, ticker)
        log_debug('Fetching %s', ticker)
        if Providers.EchoAccess:
            print('Going to {0} to fetch {1}'.format(provider_manager.Name, ticker))
        ser_list = provider_manager.fetch(series_meta)
        if dropna:
            ser_list = [x.dropna() for x in ser_list]
        if len(ser_list) > 1:
            # Not sure how more than one series will work with the SeriesMetaData
            raise NotImplementedError('More than one series in a fetch not supported')
        log('Writing %s', ticker)
        ser = ser_list[0]
        database_manager.Write(ser, series_meta)
    return ser_list[0]

def fetch_df(ticker, database='Default', dropna=True):
    """
    Return a DataFrame. Used by R.

    As a convenience for R users, dumps the last error to the log file.

    :param ticker: str
    :param database: str
    :param dropna: bool
    :return: pandas.DataFrame
    """
    try:
        ser = fetch(ticker, database, dropna)
        df = pandas.DataFrame({'series_dates': ser.index, 'series_values': ser.values})
        return df
    except:
        log_last_error()
        raise

def quick_plot(ser, title=None):
    """
    There's some overhead with plotting...
    :param ser: pandas.Series
    :return:
    """
    if plt is None:
        raise ImportError('Was not able to import plotting libraries (matplotlib.pyplot) or the converter.')
    plt.plot(ser)
    if title is None:
        title = ser.name
    plt.title(title)
    plt.grid(True)
    plt.show()


# If we have problems with initialisation, may need to not execute here - user has to call.
init_package()

def log_extension_status():
    """
    After the fact logging of what extensions were loaded. Useful for R
    :return:
    """
    log_debug('Successful Extension Initialisation')
    for e in LoadedExtensions:
        log_debug(e)
    if len(DecoratedFailedExtensions) == 0:
        log_debug('No extension loads failed.')
        return
    log_warning('Failed Extension Initialisation')
    for f,warn in DecoratedFailedExtensions:
        log_warning('Extension_File\t{0}\tMessage:\t{1}'.format(f, warn))


def _hook_fetch_external(provider_manager, ticker):
    """
    Hook for customisation when external reference is hit.
   :param provider_manager: ProviderManager
   :param ticker: str
   :return: None
   """
    pass

def log_last_error():
    """
    Convenience function to log the last error.
    :return:
    """
    msg = traceback.format_exc()
    log_error(msg)


# Do this last
LoadedExtensions, FailedExtensions, DecoratedFailedExtensions = myplatform.extensions.load_extensions()

