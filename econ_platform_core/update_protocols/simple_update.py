"""
The simplest non-trivial update protocol manager.

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
import datetime
import dateutil
import math

import econ_platform_core
from econ_platform_core.update_protocols import UpdateProtocol
from econ_platform_core.entity_and_errors import NoDataError, ConnectionError, PlatformError

class SimpleUpdate(UpdateProtocol):
    """
    Class to handle the management of data updates.

    The base class behaviour is to not update data already on the database. More
    sophisticated handlers will pushed over top of this default object during the initialisation step.

    (The more sophisticated managers will be developed in another module.)

    """
    def __init__(self):
        super().__init__(name='Simple Update')
        self.NumHours = None

    def Update(self, ticker, series_meta, provider_wrapper, database_manager):
        """
        Procedure to handle updates. The default behaviour is to not update; just retrieve from the
        database.

        :param ticker: str
        :param series_meta: econ_platform_core.SeriesMetadata
        :param provider_wrapper: econ_platform_core.ProviderWrapper
        :param database_manager: econ_platform_core.DatabaseManager
        :return:
        """
        last_refresh = series_meta.last_refresh
        ticker_str = ticker
        if last_refresh is None:
            last_refresh = database_manager.GetLastRefresh(series_meta.ticker_full)
        # If the developer is too lazy to parse strings...
        if type(last_refresh) is str:
            last_refresh = dateutil.parser.parse(last_refresh)
        nnow = datetime.datetime.now()
        if self.NumHours is None:
            self.NumHours = econ_platform_core.PlatformConfiguration['UpdateProtocol'].getint('SimpleHours')
        age = math.floor(((nnow - last_refresh).total_seconds()) / (60 * 60))
        if age < self.NumHours:
            log_debug('Series {0} not stale, going to {1}'.format(ticker_str, database_manager.Code))
            return database_manager.Retrieve(series_meta)
        else:
            # The adventure begins!
            # For now, refresh entire series.
            try:
                self.FetchAndWrite(ticker, series_meta, provider_wrapper, database_manager)
            except NoDataError:
                log_debug('Series {0} has no new data; marking refreshed'.format(ticker_str))
                database_manager.SetLastRefresh(series_meta.ticker_full)
                return database_manager.Retrieve(series_meta)
            except PlatformError as ex:
                # Unable to fetch; just retrieve from the database
                # This is perhaps too broad, but we can use whatever is in the database.
                econ_platform_core.log_last_error(just_info=True)
                print('Could not fetch from provider; using database')
                print('Explanation: ' + str(ex))
                return database_manager.Retrieve(series_meta)


