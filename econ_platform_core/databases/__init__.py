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
# from econ_platform_core import PlatformConfiguration, SeriesMetadata
#
#
# class DatabaseManager(object):
#     """
#     This is the base class for Database Managers.
#
#     Note: Only support full series replacement for now.
#     """
#     def __init__(self, name='Virtual Object'):
#         self.Name = name
#         # This is overridden by the AdvancedDatabase constructor.
#         # By extension, everything derived from this base class (like the TEXT dabase is "not advanced."
#         self.IsAdvanced = False
#         if not name == 'Virtual Object':
#             self.Code = PlatformConfiguration['DatabaseList'][name]
#         self.ReplaceOnly = True
#
#     def Find(self, ticker):
#         """
#         Can we find the ticker on the database? Default behaviour is generally adequate.
#         :param ticker: str
#         :return: SeriesMetadata
#         """
#         try:
#             provider_code, query_ticker = ticker.split('@')
#         except:
#             return self._FindLocal(ticker)
#         meta = SeriesMetadata()
#         meta.ticker_local = ''
#         meta.ticker_full = ticker
#         meta.ticker_query = query_ticker
#         meta.series_provider_code  = provider_code
#         meta.Exists = self.Exists(ticker)
#         # Provider-specific meta data data not supported yet.
#         return meta
#
#     def _FindLocal(self, local_ticker):
#         """
#         Databases that support local tickers should override this method.
#
#         :param local_ticker: SeriesMetadata
#         :return:
#         """
#         raise NotImplementedError('This database does not support local tickers')
#
#
#     def Exists(self, ticker):
#         """
#
#         :param ticker: str
#         :return: bool
#         """
#         raise NotImplementedError()
#
#     def Retrieve(self, series_meta):
#         """
#
#         :param series_meta: SeriesMetadata
#         :return: pandas.Series
#         """
#         raise NotImplementedError()
#
#     def GetMeta(self, full_ticker):
#         raise NotImplementedError()
#
#     def RetrieveWithMeta(self, full_ticker):
#         """
#         Retrieve both the meta data and the series. Have a single method in case there is
#         an optimisation for the database to do both queries at once.
#
#         Since we normally do not want the meta data at the same time, have the usual workflow to just
#         use the Retrieve() interface.
#
#         :param full_ticker: str
#         :return: list
#         """
#         meta = self.GetMeta(full_ticker)
#         ser = self.Retrieve(meta)
#         return ser, meta
#
#
#     def Write(self, ser, series_meta, overwrite=True):
#         """
#
#         :param ser: pandas.Series
#         :param series_meta: SeriesMetadata
#         :param overwrite: bool
#         :return:
#         """
#         raise NotImplementedError()