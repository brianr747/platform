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
things like matplotlib) are pushed into econ_platform, where code is meant to be loaded as extensions. If an extension
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
import webbrowser

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


def start_log(fname=None):  # pragma: nocover
    """
    Call this function if you want a log. By default, the log name is based on the base Python script name
    (sys.argv[0]), and goes into the default directory (LonInfo.LogDirectory).
    :param fname: str
    :return:
    """
    global LogInfo
    LogInfo.StartLog(fname)


PlatformConfiguration = econ_platform_core.configuration.ConfigParserWrapper()


class SeriesMetadata(PlatformEntity):
    """
    Class that holds series meta data used on the platform.

    Note: class data members were lower case so that they matched my database column naming convention.
    Probably a mistake to do it that way; should have made the database CamelCase.

    The "frequency" member is not standardised yet.

    Manifest: Standard order of "core" data fields.
    """
    Manifest = """self.Exists
self.series_id
self.series_provider_code
self.ticker_full
self.ticker_local
self.ticker_datatype
self.ticker_query
self.series_name
self.series_description
self.frequency
self.series_web_page""".replace('self.', '').split('\n')
    def __init__(self):
        # Kind of strange, but does this series yet exist on the database in question?
        super().__init__()
        self.Exists = False
        self.series_id = None
        self.series_provider_code = None
        self.ticker_full = None
        self.ticker_local = None
        self.ticker_datatype = None
        self.ticker_query = None
        self.series_name = None
        self.series_description = None
        self.series_web_page = None
        self.frequency = None
        self.ProviderMetadata = {}

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
            # noinspection PyPep8Naming
            OK = (obj is None) or (type(obj) is targ)
            if not OK:
                raise PlatformError('Invalid SeriesMetadata: {0} is not {1}'.format(attrib, targ))
        return True

    def __str__(self):
        out = ''
        for name in dir(self):
            if name.startswith('_'):
                continue
            out += '{0}\t{1}\n'.format(name, str(getattr(self, name)))
        return out

    def to_DF(self):
        """
        Return data as a DataFrame. Variable size, since provider data can vary.
        :return: pandas.DataFrame
        """
        out_index = []
        out = []
        for k in SeriesMetadata.Manifest:
            out_index.append(k)
            out.append(getattr(self, k))
        out_index.append('num_provider_data')
        if len(self.ProviderMetadata) == 0:
            self.ProviderMetadata = {'TEST_FIELD': None}
        out.append(len(self.ProviderMetadata))
        keyz = list(self.ProviderMetadata.keys())
        for k in keyz:
            out_index.append(k)
            out.append(self.ProviderMetadata[k])
        keyz.sort()
        df = pandas.DataFrame(data=out, index=out_index)
        return df



class DatabaseManager(PlatformEntity):
    """
    This is the base class for Database Managers.

    Note: Only support full series replacement for now.
    """

    def __init__(self, name='Virtual Object'):
        super().__init__()
        self.Name = name
        # This is overridden by the AdvancedDatabase constructor.
        # By extension, everything derived from this base class (like the TEXT database is "not advanced."
        self.IsAdvanced = False
        self.Code = ''
        self.ReplaceOnly = True

    def Find(self, ticker):
        """
        Can we find the ticker on the database? Default behaviour is generally adequate.
        :param ticker: str
        :return: SeriesMetadata
        """
        ticker_obj = econ_platform_core.tickers.map_string_to_ticker(ticker)
        if type(ticker_obj) is TickerLocal:
            return self._FindLocal(ticker_obj)
        if type(ticker_obj) is TickerDataType:
            return self._FindDataType(ticker_obj)
        meta = SeriesMetadata()
        meta.ticker_local = None
        meta.ticker_full = ticker_obj
        meta.series_provider_code, meta.ticker_query = ticker_obj.SplitTicker()
        meta.Exists = self.Exists(meta)
        # Provider-specific meta data data not supported yet.
        return meta

    def _FindLocal(self, local_ticker):  # pragma: nocover
        """
        Databases that support local tickers should override this method.

        :param local_ticker: TickerLocal
        :return:
        """
        raise NotImplementedError('This database does not support local tickers')

    def _FindDataType(self, datatype_ticker):  # pragma: nocover
        """

        :param datatype_ticker: TickerDataType
        :return:
        """
        raise NotImplementedError('This database does not support data type tickers')

    def Exists(self, ticker):  # pragma: nocover
        """

        :param ticker: econ_platform_core.tickers._TickerAbstract
        :return: bool
        """
        raise NotImplementedError()

    def Retrieve(self, series_meta):  # pragma: nocover
        """

        :param series_meta: SeriesMetadata
        :return: pandas.Series
        """
        raise NotImplementedError()

    def GetMeta(self, full_ticker):  # pragma: nocover
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

    def Delete(self, series_meta):  # pragma: nocover
        """
        Delete a series.
        :param series_meta: SeriesMetadata
        :return:
        """
        raise NotImplementedError()

    def Write(self, ser, series_meta, overwrite=True):  # pragma: nocover
        """

        :param ser: pandas.Series
        :param series_meta: SeriesMetadata
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

    def AddDatabase(self, wrapper, code=None):
        """
        Add a database. If the code is not supplied, uses the code based on the PlatformConfiguration
        setting (normal use). Only need to supply the code for special cases, like having extra SQLite
        database files for testing.

        :param wrapper: DatabaseManager
        :param code: str
        :return:
        """
        if code is None:
            code = PlatformConfiguration['DatabaseList'][wrapper.Name]
        wrapper.Code = code
        self.DatabaseDict[wrapper.Code] = wrapper

    def __getitem__(self, item):
        """
        Access method.

        :param item: str
        :return: DatabaseManager
        """
        if item.upper() == 'DEFAULT':
            item = PlatformConfiguration['Database']['Default']
        if item == 'SQL':
            # If the DEFAULT is SQL, will be re-mapped twice!
            item = PlatformConfiguration['Database']['SQL']
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
        # Sometimes we fetch an entire table as a side effect of fetching a series.
        # A provider can mark this possibility by setting TableWasFetched to True, and
        # loading up TableSeries, TableMeta with series/meta-data. The fetch() function will
        # store the data.
        self.TableWasFetched = False
        self.TableSeries = {}
        self.TableMeta = {}
        self.WebPage = ''
        if not name == 'VirtualObject':
            self.ProviderCode = PlatformConfiguration['ProviderList'][name]

    def fetch(self, series_meta):  # pragma: nocover
        """
        Fetch a series from a provider.

        :param series_meta: SeriesMetadata
        :return: pandas.Series
        """
        raise NotImplementedError

    def GetSeriesURL(self, series_meta):
        """
        Get the URL for a series, if possible. Otherwise, returns the provider webpage.

        :param series_meta: SeriesMetadata
        :return: str
        """
        try:
            return self._GetSeriesUrlImplementation(series_meta)
        except NotImplementedError:
            return self.WebPage

    def _GetSeriesUrlImplementation(self, series_meta):
        """
        Implements the actual fetching. If a NotImplementedError is thrown, the object will return the
        Provider.WebPage.
        """
        raise NotImplementedError()


class ProviderList(PlatformEntity):
    """
    List of all provider wrappers. Developers can push their own DatabaseManagers into the global object.

    Keep the "User" provider also saved as a data member, since it will be accessed by code hooking into it.
    """

    def __init__(self):
        super().__init__()
        self.ProviderDict = {}
        self.EchoAccess = False
        self.UserProvider = None

    def Initialise(self):
        self.EchoAccess = PlatformConfiguration['ProviderOptions'].getboolean('echo_access')

    def AddProvider(self, obj):
        """
         Add a provider
         :param obj: ProviderWrapper
         :return:
         """
        self.ProviderDict[obj.ProviderCode] = obj
        if obj.Name == 'User':
            # Tuck the "User" provider into a known location.
            self.UserProvider = obj

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

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def Update(self, series_meta, provider_wrapper, database_manager):
        """
        Procedure to handle updates. The default behaviour is to not update; just retrieve from the
        database.

        :param series_meta: SeriesMetadata
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
    :return: pandas.Series
    """
    # Default handling is inide the database manager...
    # if database.lower() == 'default':
    #     database = PlatformConfiguration["Database"]["Default"]
    database_manager: DatabaseManager = Databases[database]
    series_meta = database_manager.Find(ticker)
    series_meta.AssertValid()
    provider_code = series_meta.series_provider_code
    # noinspection PyPep8
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
        # Force this to False, so that ProviderManager extension writers do not need to
        # remember to do so.
        provider_manager.TableWasFetched = False
        if Providers.EchoAccess:
            print('Going to {0} to fetch {1}'.format(provider_manager.Name, ticker))
        try:
            out = provider_manager.fetch(series_meta)
        except TickerNotFoundError:
            # If the table was fetched, write the table, even if the specific series was not there...
            if provider_manager.TableWasFetched:
                for k in provider_manager.TableSeries:
                    t_ser = provider_manager.TableSeries[k]
                    t_meta = provider_manager.TableMeta[k]
                    # Don't write the single series again..
                    if str(t_meta.ticker_full) == str(series_meta.ticker_full):
                        continue
                    database_manager.Write(t_ser, t_meta)
            raise
        if type(out) is not tuple:
            ser = out
        else:
            ser, series_meta = out
        if dropna:
            ser = ser.dropna()
        log('Writing %s', ticker)
        database_manager.Write(ser, series_meta)
        if provider_manager.TableWasFetched:
            for k in provider_manager.TableSeries:
                t_ser = provider_manager.TableSeries[k]
                t_meta = provider_manager.TableMeta[k]
                # Don't write the single series again..
                if str(t_meta.ticker_full) == str(series_meta.ticker_full):
                    continue
                database_manager.Write(t_ser, t_meta)

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
    # noinspection PyPep8
    try:
        ser = fetch(ticker, database, dropna)
        df = pandas.DataFrame({'series_dates': ser.index, 'series_values': ser.values})
        return df
    except:
        log_last_error()
        raise


def log_extension_status():  # pragma: nocover
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
    for f, warn in DecoratedFailedExtensions:
        log_warning('Extension_File\t{0}\tMessage:\t{1}'.format(f, warn))


# noinspection PyUnusedLocal
def _hook_fetch_external(provider_manager, ticker):
    """
    Hook for customisation when external reference is hit.
   :param provider_manager: ProviderManager
   :param ticker: str
   :return: None
   """
    pass


def log_last_error():  # pragma: nocover
    """
    Convenience function to log the last error.
    :return:
    """
    msg = traceback.format_exc()
    log_error(msg)

def get_provider_url(provider_code, open_browser=True):
    """
    Get the URL of the provider's data website, if it exists (specified).

    Returns None if not defined.

    Will open a browser if asked.

    :param provider_code: str
    :return: str
    """
    provider_code = str(provider_code)
    try:
        url = Providers[provider_code].WebPage
    except KeyError:
        raise PlatformError('Provider code not defined: {0}'.format(provider_code))
    if url is None or len(url) == 0:
        return None
    if open_browser:
        webbrowser.open(url, new=2)
    return url


def get_series_URL(ticker, database='Default', open_browser=True):
    database_manager: DatabaseManager = Databases[database]
    series_meta = database_manager.Find(ticker)
    provider_code = str(series_meta.series_provider_code)
    try:
        url = Providers[provider_code].GetSeriesURL(series_meta)
    except KeyError:
        raise PlatformError('Provider code not defined: {0}'.format(provider_code))
    if url is None or len(url) == 0:
        return None
    if open_browser:
        webbrowser.open(url, new=2)
    return url


def fetch_metadata(ticker_str, database='SQL'):
    """
    Given a ticker string, find the series metadata, returned as a pandas.DataFrame.

    TODO: If does not exist, try to go to the provider.

    :param ticker_str: str
    :param database: str
    :return: pandas.DataFame
    """
    db_manager: DatabaseManager = Databases[database]
    meta = db_manager.Find(ticker_str)
    if meta.Exists:
        try:
            meta = db_manager.GetMeta(meta.ticker_full)
        except NotImplementedError:
            pass
    df = meta.to_DF()
    return df


def init_package():
    """
    Call to initialise the package, other than configuration file (and logging set up).
    :return:
    """
    global PlatformConfiguration
    if not PlatformConfiguration.LoadedAny:
        # May switch over to "silent" loading, but not knowing which config files were loaded can
        # cause a lot of errors...
        PlatformConfiguration = econ_platform_core.configuration.load_platform_configuration(display_steps=True)
    # By default, go into the "logs" directory below this file.
    if len(LogInfo.LogDirectory) == 0:
        # If it has not been set manually, use the config information.
        LogInfo.LogDirectory = utils.parse_config_path(PlatformConfiguration['Logging']['LogDirectory'])
    Databases.Initialise()
    Providers.Initialise()
    UpdateProtocolList.Initialise()
    # Replace this with an "extension manager"
    global LoadedExtensions
    global FailedExtensions
    global DecoratedFailedExtensions
    LoadedExtensions, FailedExtensions, DecoratedFailedExtensions = econ_platform_core.extensions.load_extensions()


def get_platform_information(return_instead_of_print=False):
    """
    If return_instead_of_print is True, returns a DataFrame with information,
    otherwise just prints to console (expected usage).

    Format will change, so this is just for users who want to refresh their memory of provider codes, see
    what extensions exist, etc.

    :return: pandas.DataFrame
    """
    out = pandas.DataFrame(columns=['Type', 'Name', 'Info'])
    # Create a little utility to append rows to a DataFrame
    def appender(df, row):
        return df.append(pandas.DataFrame([row], columns=df.columns))
    # First: extensions
    for ext in LoadedExtensions:
        out = appender(out, ['Extension', ext, 'Loaded'])
    out.sort_values('Name')
    failed = pandas.DataFrame(columns=['Type', 'Name', 'Info'])
    for ext in FailedExtensions:
        failed = appender(failed, ['Extension', ext, 'FAILED'])
    out = failed.append(out)
    # Databases
    db_list = list(Databases.DatabaseDict.keys())
    db_list.sort()
    for db in db_list:
        mgr = Databases[db]
        out = appender(out, ['Database', mgr.Name, db])
    prov_list = list(Providers.ProviderDict.keys())
    prov_list.sort()
    for prov in prov_list:
        provider = Providers[prov]
        out = appender(out, ['Provider', provider.Name, prov])

    out.index = list(range(0, len(out.index)))
    if return_instead_of_print:
        return out
    else:
        print(out)
