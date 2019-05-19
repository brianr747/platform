"""
hook_provider_dbnomics.py

Functions to fetch data from DBNomics, and convert to standard format.

In this case, convert pandas data frames into a list of time series.


The challenge for our purposes is coming up with a common interface for the more advanced queries
the DBnmonics interface supports.

Examples taken from the dnomics package __init__.py:
   - fetch one series:
      fetch_series("AMECO/ZUTN/EA19.1.0.0.0.ZUTN")

    - fetch all the series of a dataset:
      fetch_series("AMECO", "ZUTN")

    - fetch many series from different datasets:
      fetch_series(["AMECO/ZUTN/EA19.1.0.0.0.ZUTN", "AMECO/ZUTN/DNK.1.0.0.0.ZUTN", "IMF/CPI/A.AT.PCPIT_IX"])

    - fetch many series from the same dataset, searching by dimension:
      fetch_series("AMECO", "ZUTN", dimensions={"geo": ["dnk"]})

    - fetch many series from the same dataset, searching by code mask:
      fetch_series("IMF", "CPI", series_code="M.FR+DE.PCPIEC_WT")

For now, will just support a list of series. Will need to look at how to come up with a common interface
for "table queries" across providers.


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

import dbnomics
import pandas
import numpy

import econ_platform_core


class ProviderDBnomics(econ_platform_core.ProviderWrapper):
    def __init__(self):
        super(ProviderDBnomics, self).__init__(name='DBnomics')
        self.WebPage = 'http://www.bondeconomics.com'

    def _GetSeriesUrlImplementation(self, series_meta):
        """
        Get the URL for a series.

        :param series_meta: econ_platform_core.SeriesMetadata
        :return:
        """
        ticker = str(series_meta.ticker_query)
        url = 'https://db.nomics.world/{0}'.format(ticker)
        return url

    def fetch(self, series_meta):
        """"
        Initial stab at querying. Will refactor code into a subclass...

        Can only support single series queries...
        :param series_meta: econ_platform_core.SeriesMetadata
        :return: list
        """
        query_ticker = str(series_meta.ticker_query)
        df = dbnomics.fetch_series(query_ticker)
        tickers = set(df.series_code)
        if len(tickers) > 1:
            raise NotImplementedError('Multiple series queries not yet supported')
        ser = pandas.Series(df.value)
        ser.index = df.period
        ser.name = '{0}@{1}/{2}/{3}'.format(self.ProviderCode, df['provider_code'][0], df['dataset_code'][0],
                                             df['series_code'][0])
        # Convert 'NA' to NaN
        ser = ser.replace('NA', numpy.nan)
        # Always return a list of series. Only the user interface will convert list to a single pandas.Series
        # Get metadata
        colz = df.columns
        if 'FREQUENCY' in colz:
            series_meta.frequency = df['FREQUENCY'][df.index[0]]
        if 'series_name' in colz:
            series_meta.series_name = df['series_name'][df.index[0]]
            series_meta.series_description = '{0} : DB.nomics series {1}'.format(series_meta.series_name,
                                                                                 query_ticker)
        excluded = ('value', 'period', 'original_period', 'indexed_at')
        for c in colz:
            if c in excluded:
                continue
            series_meta.ProviderMetadata[c] = df[c][df.index[0]]

        return ser




