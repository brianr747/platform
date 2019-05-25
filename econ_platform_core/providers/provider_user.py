"""
Provider for internally generated series.

By default, empty, but the idea is that you push your own handlers into this object. Probably need to monkey-patch
your own class if this gets complicated.

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

import econ_platform_core
import econ_platform_core.entity_and_errors


class ProviderUser(econ_platform_core.ProviderWrapper):
    def __init__(self):
        super(ProviderUser, self).__init__(name='User')
        self.SeriesMapper = {}

    def MapTicker(self, query_ticker):
        """
        Monkey patch this method if you have a complex set of user functions
        :param query_ticker: str
        :return:
        """
        try:
            return self.SeriesMapper[str(query_ticker)]
        except KeyError:
            raise econ_platform_core.entity_and_errors.TickerNotFoundError(
                'There is no function that handles the query ticker: {0}'.format(query_ticker)) from None


    def fetch(self, series_meta):
        """
        Get a series
        :param series_meta: econ_platform_core.SeriesMetadata
        :return: pandas.Series
        """
        query_ticker = series_meta.ticker_query
        fn = self.MapTicker(query_ticker)
        ser = fn(series_meta)
        return ser
