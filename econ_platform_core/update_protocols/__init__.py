"""
Directory to hold update protocols.

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
from logging import debug as log_debug

import econ_platform_core
from econ_platform_core import PlatformEntity, PlatformError, TickerNotFoundError


class UpdateProtocol(PlatformEntity):
    """
    Base class for update protocol managers.
    """
    def __init__(self, name='Abstract Base UpdateProtocol Class'):
        super().__init__()
        self.Name = name

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def Update(self, ticker, series_meta, provider_wrapper, database_manager):
        """
        Procedure to handle updates. The default behaviour is to not update; just retrieve from the
        database.

        :param ticker: str
        :param series_meta: SeriesMetadata
        :param provider_wrapper: ProviderWrapper
        :param database_manager: DatabaseManager
        :return:
        """
        raise NotImplementedError()

    def FetchAndWrite(self, ticker, series_meta, provider_manager, database_manager):
        """
        Fetch a series from an external provider, and write it to the database. Should not
        need to override this method.

        :param ticker: str
        :param series_meta: econ_platform_core.SeriesMetaData
        :param provider_manager: econ_platform_core.ProviderWrapper
        :param database_manager: econ_platform_core.DatabaseManager
        :return:
        """
        if provider_manager.IsExternal:
            _hook_fetch_external(provider_manager, ticker)
        if provider_manager.PushOnly:
            raise PlatformError(
                'Series {0} does not exist on {1}. Its ticker indicates that it is push-only series.'.format(
                   ticker, database_manager.Code)) from None
        log_debug('Fetching %s', ticker)
        # Force this to False, so that ProviderManager extension writers do not need to
        # remember to do so.
        provider_manager.TableWasFetched = False
        if econ_platform_core.Providers.EchoAccess:
            print('Going to {0} to fetch {1}'.format(provider_manager.Name, ticker))
        try:
            out = provider_manager.fetch(series_meta)
        except TickerNotFoundError:
            # If the table was fetched, write the table, even if the specific series was not there...
            if provider_manager.TableWasFetched:
                self.WriteTable(provider_manager, database_manager)
            raise
        if type(out) is not tuple:
            ser = out
        else:
            ser, series_meta = out
        ser = ser.dropna()
        log_debug('Writing %s', ticker)
        if not provider_manager.TableWasFetched:
            database_manager.Write(ser, series_meta)
            if not database_manager.SetsLastUpdateAutomatically:
                database_manager.SetLastUpdate(series_meta.ticker_full)
        else:
            self.WriteTable(provider_manager, database_manager)
        return ser

    @staticmethod
    def WriteTable(provider_manager, database_manager):
        for k in provider_manager.TableSeries:
            t_ser = provider_manager.TableSeries[k]
            t_meta = provider_manager.TableMeta[k]
            database_manager.Write(t_ser, t_meta)
            if not database_manager.SetsLastUpdateAutomatically:
                database_manager.SetLastUpdate(t_meta.ticker_full)



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
        self.Default = 'NOUPDATE'

    def __getitem__(self, item):
        """
        Get the protocol via indexing. "DEFAULT" (case-insensitive) is mapped to self.Default.
        (fetch() will call DEFAULT.)
        :param item: UpdateProtocol
        :return:
        """
        if item.lower() == 'default':
            item = self.Default
        try:
            return self.Protocols[item]
        except KeyError:
            raise PlatformError('Unknown UpdateProtocol code: {0}'.format(item))

    def Initialise(self):
        """
        Get the NOUPDATE protocol manager
        :return:
        """
        self.Protocols['NOUPDATE'] = NoUpdateProtocol()
        self.Default = econ_platform_core.PlatformConfiguration['UpdateProtocol']['Default']


class NoUpdateProtocol(UpdateProtocol):
    """
    Class to handle the management of data updates.

    The base class behaviour is to not update data already on the database. More
    sophisticated handlers will pushed over top of this default object during the initialisation step.

    (The more sophisticated managers will be developed in another module.)

    """
    def __init__(self):
        super().__init__(name='No Updates For You!')

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def Update(self, ticker, series_meta, provider_wrapper, database_manager):
        """
        Procedure to handle updates. The default behaviour is to not update; just retrieve from the
        database.

        :param ticker: str
        :param series_meta: SeriesMetadata
        :param provider_wrapper: ProviderWrapper
        :param database_manager: DatabaseManager
        :return:
        """
        log_debug('Fetching {0} from {1}'.format(ticker, database_manager.Name))
        return database_manager.Retrieve(series_meta)


def _hook_fetch_external(provider_manager, ticker):
    pass
