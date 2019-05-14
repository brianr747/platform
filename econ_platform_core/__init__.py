"""
econ_platform_core - Glue code for a unified work environment.

The center-piece of the package is *fetch()* a function which dynamically loads a pandas time series (Series object)
from any supported provider or database interface. The fetch command will determine whether the series exists in the
local database, or whether to query the external provider. If it already exists, the platform will decide whether it
is time to seek a refresh. (NOTE: That update protocol is not implemented at the time of writing.)

For a user, this is all done "under the hood" within a single line of code. The same plotting routines will always
work, even if the computer is cut off from external providers and the user has to grab locally archived data.

Normally, users will import econ_platform and call init_econ_platform(), which will
initialise this package.

Importing this file alone is supposed to have minimal side effects. However, configuration information is not
loaded, and so most functions will crash. This means that end uses will almost always want to call the initialisation
function (or import econ_platform.start, which is a script that initialises the platform).

This package is supposed to only depend on standard Python libraries and *pandas*. Anything else (including
thinge like matplotlib) are pushed into econ_platform, where code is meant to be loaded as extesnions. If an extension
cannot be loaded (missing API packages, for example), econ_platform will still load up, it will just report that
an extension load failed.

Since sqlite3 is in the standard Python libraries, base SQL functionality will be implemented here.

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

import pandas
import traceback
import configparser

# As a convenience, use the "logging.info" function as log.
from logging import info as log, debug as log_debug, warning as log_warning, error as log_error


import econ_platform_core.configuration
from econ_platform_core.utils import PlatformEntity
from econ_platform_core import utils as utils
import econ_platform_core.extensions

from econ_platform_core.tickers import TickerFull, TickerDataType, TickerFetch, TickerLocal, TickerProviderCode

import econ_platform_core.tickers



# Get the logging information. Users can either programmatically change the LogInfo.LogDirectory or
# use a config file before calling start_log()
from econ_platform_core.utils import PlatformEntity

LogInfo = utils.PlatformLogger()

def start_log(fname=None):
    """
    Call this function if you want a log. By default, the log name is based on the base Python script name
    (sys.argv[0]), and goes into the default directory (LonInfo.LogDirectory).
    :param fname: str
    :return:
    """
    global LogInfo
    LogInfo.StartLog(fname)


PlatformConfiguration = econ_platform_core.configuration.ConfigParserWrapper()

class SeriesMetaData(PlatformEntity):
    """
    Class that holds series meta data used on the platform.
    """
    def __init__(self):
        # Kind of strange, but does this series yet exist on the database in question?
        super().__init__()
        self.Exists = False
        self.series_id = -1
        self.series_provider_code = ''
        self.ticker_full = ''
        self.ticker_local = ''
        self.ticker_datatype = ''
        self.ticker_query = ''
        self.series_name = None
        self.series_description = None
        self.ProviderMetaData = {}

    def AssertValid(self):
        """
        Are tickers valid? Use this call defensively to force internal calls to use the Ticker objects,
        not strings.

        Tickers can either be empty strings, or else of the valid ticker type.
        :return:
        """
        things_to_test = (('series_provider_code', TickerProviderCode),
                          ('ticker_full', TickerFull),
                          ('ticker_local', TickerLocal),
                          ('ticker_datatype', TickerDataType),
                          ('ticker_query', TickerFetch))
        for attrib, targ in things_to_test:
            obj = getattr(self, attrib)
            OK = (len(str(obj)) == 0) or (type(obj) is targ)
            if not OK:
                raise PlatformError('Invalid SeriesMetaData: {0} is not {1}'.format(attrib, targ))
        return True

    def __str__(self):
        out = ''
        for name in dir(self):
            if name.startswith('_'):
                continue
            out += '{0}\t{1}\n'.format(name, str(getattr(self, name)))
        return out


class DatabaseManager(PlatformEntity):
    """
    This is the base class for Database Managers.

    Note: Only support full series replacement for now.
    """
    def __init__(self, name='Virtual Object'):
        super().__init__()
        self.Name = name
        # This is overridden by the AdvancedDatabase constructor.
        # By extension, everything derived from this base class (like the TEXT dabase is "not advanced."
        self.IsAdvanced = False
        self.Code = ''
        self.ReplaceOnly = True

    def Find(self, ticker):
        """
        Can we find the ticker on the database? Default behaviour is generally adequate.
        :param ticker: str
        :return: SeriesMetaData
        """
        ticker_obj = econ_platform_core.tickers.map_string_to_ticker(ticker)
        if type(ticker_obj) is TickerLocal:
            return self._FindLocal(ticker_obj)
        if type(ticker_obj) is TickerDataType:
            return self._FindDataType(ticker_obj)
        meta = SeriesMetaData()
        meta.ticker_local = ''
        meta.ticker_full = ticker_obj
        meta.series_provider_code, meta.ticker_query = ticker_obj.SplitTicker()
        meta.Exists = self.Exists(meta)
        # Provider-specific meta data data not supported yet.
        return meta

    def _FindLocal(self, local_ticker):
        """
        Databases that support local tickers should override this method.

        :param local_ticker: TickerLocal
        :return:
        """
        raise NotImplementedError('This database does not support local tickers')

    def _FindDataType(self, datatype_ticker):
        """

        :param datatype_ticker: TickerDataYype
        :return:
        """
        raise NotImplementedError('This database does not support data type tickers')


    def Exists(self, ticker):
        """

        :param ticker: econ_platform_core.tickers._TickerAbstract
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
        meta.AssertValid()
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

class DatabaseList(PlatformEntity):
    """
    List of all Database managers. Developers can push their own DatabaseManagers into the global object.
    """
    def __init__(self):
        super().__init__()
        self.DatabaseDict = {}

    def Initialise(self):
        pass

    def AddDatabase(self, wrapper):
        """

        :param wrapper: DatabaseManager
        :return:
        """
        code = PlatformConfiguration['DatabaseList'][wrapper.Name]
        wrapper.Code = code
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


class ProviderWrapper(PlatformEntity):
    """
    Data provider class. Note that we call them "providers" and not "sources" since the source is the
    agency in the real world that calculates the data. The provider and the source can be the same - for example,
    if we get Eurostat data from Eurostat itself. However, we can get Eurostat data from DB.nomics.

    """
    Name: str

    def __init__(self, name='VirtualObject'):
        super().__init__()
        self.Name = name
        self.ProviderCode = ''
        self.IsExternal = True
        if not name == 'VirtualObject':
            self.ProviderCode = PlatformConfiguration['ProviderList'][name]

    def fetch(self, series_meta):
        raise NotImplementedError


class ProviderList(PlatformEntity):
    """
    List of all proviser wrappers. Developers can push their own DatabaseManagers into the global object.
    """
    def __init__(self):
        super().__init__()
        self.ProviderDict = {}
        self.EchoAccess = False

    def Initialise(self):
        self.EchoAccess = PlatformConfiguration['ProviderOptions'].getboolean('echo_access')

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
        # Need to convert to string since we are likely passed a ticker.
        return self.ProviderDict[str(item)]


Providers = ProviderList()

# TODO: Replace these variables with an "Extension Manager".
LoadedExtensions = []
FailedExtensions = []
DecoratedFailedExtensions = []


class PlatformError(Exception):
    pass

class TickerError(PlatformError):
    pass

class TickerNotFoundError(PlatformError):
    pass


class UpdateProtocol(PlatformEntity):
    """
    Class to handle the management of data updates.

    The base class behaviour is to not update data already on the database. More
    sophisticated handlers will pushed over top of this default object during the initialisation step.

    (The more sophisticated managers will be developed in another module.)

    """
    def Update(self, series_meta, provider_wrapper, database_manager):
        """
        Procedure to handle updates. The default behaviour is to not update; just retrieve from the
        database.

        :param series_meta: SeriesMetaData
        :param provider_wrapper: ProviderWrapper
        :param database_manager: DatabaseManager
        :return:
        """
        log_debug('Fetching {0} from {1}'.format(series_meta.ticker_full, database_manager.Name))
        return database_manager.Retrieve(series_meta)


class UpdateProtocolManager(PlatformEntity):
    """
    Base class for series update protocols.

    Implements the 'NOUPDATE' protocol, which unsurprisingly, never updates series.

    Add subclasses to the UpdateProtocolList to offer more interesting options.

    Eventually, need to offer the ability to choose which to use. Since we only have one option,
    not needed...
    """
    def __init__(self):
        super().__init__()
        self.Protocols = {}

    def __getitem__(self, item):
        """

        :param item: UpdateProtocol
        :return:
        """
        try:
            return self.Protocols[item]
        except KeyError:
            raise PlatformError('Unknown UpdateProtocol code: {0}'.format(item))

    def Initialise(self):
        """
        Get the NOUPDATE protocol manager
        :return:
        """
        self.Protocols['NOUPDATE'] = UpdateProtocol()


UpdateProtocolList = UpdateProtocolManager()


def fetch(ticker, database='Default', dropna=True):
    """
    Fetch a series from database; may create series and/or update as needed.

    (May create a "fetchmany()" for fancier fetches that take a slice of the database.)

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
    series_meta.AssertValid()
    provider_code = series_meta.series_provider_code
    try:
        provider_manager: ProviderWrapper = Providers[provider_code]
    except:
        raise KeyError('Unknown provider_code: ' + str(provider_code))

    if series_meta.Exists:
        # Return what is on the database.
        global UpdateProtocolList
        # TODO: Allow for choice of protocol.
        return UpdateProtocolList["NOUPDATE"].Update(series_meta, provider_manager, database_manager)
    else:
        if provider_manager.IsExternal:
            _hook_fetch_external(provider_manager, ticker)
        log_debug('Fetching %s', ticker)
        if Providers.EchoAccess:
            print('Going to {0} to fetch {1}'.format(provider_manager.Name, ticker))
        ser = provider_manager.fetch(series_meta)
        if dropna:
            ser = ser.dropna()
        log('Writing %s', ticker)
        database_manager.Write(ser, series_meta)
    return ser


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


def init_package(configuration_wrapper=None):
    """
    Call to initialise the package, other than configuration file (and logging set up).
    :param configuration_wrapper: econ_platform_core.configuration.ConfigParserWrapper
    :return:
    """
    global PlatformConfiguration
    if not PlatformConfiguration.LoadedAny:
        try:
            # It would be good to log the loading of configuration information, except that the logging
            # configuration is loaded in this step!
            # Try to load configuration silently...
            PlatformConfiguration = econ_platform_core.configuration.load_platform_configuration(display_steps=True)
        except:
            raise
            # it failed, so try again, showing the steps...
            # PlatformConfiguration = econ_platform_core.configuration.load_platform_configuration(display_steps=True)
    # By default, go into the "logs" directory below this file.
    if len(LogInfo.LogDirectory) == 0:
        # If it has not been set manually, use the config information.
        LogInfo.LogDirectory = utils.parse_config_path(PlatformConfiguration['Logging']['LogDirectory'])
    Databases.Initialise()
    Providers.Initialise()
    UpdateProtocolList.Initialise()
    global LoadedExtensions
    global FailedExtensions
    global DecoratedFailedExtensions
    LoadedExtensions, FailedExtensions, DecoratedFailedExtensions = econ_platform_core.extensions.load_extensions()
