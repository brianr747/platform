"""

Database managers.

Minimal implementation

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

# Ran into circular import problems, so the base database class went into econ_platform_core.__init__.py. I might try
# to move it back later. I might make a stub definition.
import warnings

import econ_platform_core
import econ_platform_core.entity_and_errors
from econ_platform_core.series_metadata import SeriesMetadata
from econ_platform_core.tickers import TickerFull, TickerProviderCode, TickerLocal, TickerFetch, TickerDataType

class AdvancedDatabase(econ_platform_core.DatabaseManager):
    """
    Abstract base class for all "advanced" databases; assumed to have at least the functionality of SQL databases.
    However, no assumption that SQL is under the hood.

    Handles high level logic.

    This class exposes an interface of public methods (no underscore), with the work done in methods designed
    to be overloaded (with underscores).

    Since we can have a half dozen database classes lying around in the code base, they cannot connect on the
    package initialisation step. We also cannot guarantee that any particular public function is called first.
    Therefore, all the public methods have to check to see whether the HandleDatabase has been initialised.

    "HandleDatabase" is used rather than "Connection" since it may not be an actual SQL Connection object in
    implementations. If you do not want to use that member, just set it to anything other than None when you initialise
    the connection.
    """
    def __init__(self, name='Advanced Database (Abstract)'):
        super().__init__(name=name)
        self.IsAdvanced = True
        self.HandleDatabase = None

    def Connect(self):
        """
        Connect to the database, if HandleDatabase is None.
        :return:
        """
        if self.HandleDatabase is not None:
            return
        # If this fails, subclass should throw useful ConnectionError.
        self._Connect()
        if self.HandleDatabase is None:
            raise econ_platform_core.entity_and_errors.ConnectionError('Database handle not set!')

    def _Connect(self):
        """
        Subclasses override this. Make sure that HandleDatabase is not None.

        Should throw a descriptive ConnectionError if failure.

        :return:
        """
        raise NotImplementedError()

    def Find(self, ticker_str):
        """
        Find metadata based on a ticker string. Note that it can be a full ticker, local ticker, or datatype ticker.

        This method is identical (now) to GetMeta(), and one of them will be deprecated. I think GetMeta() is a better
        name, and so it will likely survive.

        :param ticker_str: str
        :return: econ_platform_core.SeriesMeta
        """
        warnings.warn('Find is being replaced by GetMeta()', DeprecationWarning)
        return self.GetMeta(ticker_str)
        # self.Connect()
        # ticker_obj = econ_platform_core.tickers.map_string_to_ticker(ticker_str)
        # if type(ticker_obj) is TickerLocal:
        #     return self._GetMetaFromLocalTicker(ticker_obj)
        # if type(ticker_obj) is TickerDataType:
        #     return self._FindDataType(ticker_obj)
        # if type(ticker_obj) is TickerFull:
        #     return self._GetMetaFromFullTicker(ticker_obj)
        # raise econ_platform_core.PlatformError('Internal error: unsupported ticker class')

    def Exists(self, ticker_string):
        """
        Does a ticker exist?
        :param ticker_string: str
        :return: bool
        """
        self.Connect()
        return self._Exists(ticker_string)

    def _Exists(self, ticker_string):
        """
        Implements Exists(). This implementation calls GetMeta(), but could be replaced by something
        more efficient (since everything other than the Exists property is thrown out).

        (It is unclear whether this method is needed...)
        :return: bool
        """
        meta = self.GetMeta(ticker_string)
        return meta.Exists

    def GetMeta(self, ticker_string):
        """
        Does the same thing as Find(). Ouch. One method will be deprecated.
        :param ticker_string: str
        :return: SeriesMetadata
        """
        self.Connect()
        ticker_obj = econ_platform_core.tickers.map_string_to_ticker(ticker_string)
        if type(ticker_obj) is TickerLocal:
            return self._GetMetaFromLocalTicker(ticker_obj)
        if type(ticker_obj) is TickerDataType:
            return self._FindDataType(ticker_obj)
        if type(ticker_obj) is TickerFull:
            return self._GetMetaFromFullTicker(ticker_obj)
        raise econ_platform_core.entity_and_errors.PlatformError('Internal error: unsupported ticker class')

    def _GetMetaFromFullTicker(self, ticker_full):
        """
        Get the meta data based on the full ticker.

        :param ticker_full: TickerFull
        :return: SeriesMetadata
        """
        raise NotImplementedError()

    def _GetMetaFromLocalTicker(self, ticker_local):
        """
        Given the local ticker, get the metadata object.

        :param ticker_local: TickerLocal
        :return: SeriesMetadata
        """
        raise NotImplementedError()

    def _GetMetaFromDatatypeTicker(self, ticker_datatype):
        """
        Given a datatype ticker, return the SeriesMeta object.

        :param ticker_datatype: TickerDatatype
        :return: SeriesMeta
        """
        raise NotImplementedError()



