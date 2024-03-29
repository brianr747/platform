"""
Text "database"


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

import os
import pandas
import datetime
import pathlib

import econ_platform_core
import econ_platform_core.databases
import econ_platform_core.entity_and_errors
import econ_platform_core.series_metadata
import econ_platform_core.utils


class DatabaseText(econ_platform_core.DatabaseManager):
    """
    Database that dumps time series into a folder. Simple and effective. No metadata.


    """
    def __init__(self):
        super().__init__('Text File Database')
        self.Directory = None
        # The timestamp is automatically set by the OS when writing.
        self.SetsLastUpdateAutomatically = True

    def CheckDirectory(self):
        if self.Directory is None:
            self.Directory = econ_platform_core.utils.parse_config_path(
                econ_platform_core.PlatformConfiguration['D_TEXT']['directory'])

    def GetFileName(self, ticker_full, full_path=True):
        """
        Get the file name associated with a ticker.
        :param ticker_full: TickerFull
        :param full_path: bool
        :return: str
        """
        # This looks crazy, but might get passes a SeriesMeta by accident. My code convention switched around during
        # development...
        if hasattr(ticker_full, 'ticker_full'):
            ticker_full = ticker_full.ticker_full
        file_only = econ_platform_core.utils.convert_ticker_to_variable(str(ticker_full)) + '.txt'
        if full_path:
            return os.path.join(self.Directory, file_only)
        else:
            return file_only

    def Exists(self, ticker_full):
        self.CheckDirectory()
        full_file = self.GetFileName(ticker_full, full_path=True)
        return os.path.exists(full_file)

    def Retrieve(self, series_meta):
        self.CheckDirectory()
        full_name = self.GetFileName(series_meta, full_path=True)
        econ_platform_core.log_debug('Loading from %s', full_name)
        df = pandas.read_csv(filepath_or_buffer=full_name, sep='\t', parse_dates=True, index_col=0)
        ser = pandas.Series(df[df.columns[0]])
        return ser

    def _GetMetaFromFullTicker(self, full_ticker):
        self.CheckDirectory()
        full_name = self.GetFileName(full_ticker, full_path=True)
        if not os.path.exists(full_name):
            raise econ_platform_core.entity_and_errors.TickerNotFoundError('Unknown ticker: {0}'.format(full_ticker))
        return self.GetMetaFromFile(full_name)

    def GetMetaFromFile(self, full_name):
        # Just read the first line.
        f = open(full_name, 'r')
        header = f.readline()
        header = header.rstrip()
        try:
            dummy, full_ticker = header.split('\t')
        except:
            raise econ_platform_core.entity_and_errors.PlatformError('Corrupt file: {0}'.format(full_name))
        meta = econ_platform_core.series_metadata.SeriesMetadata()
        meta.ticker_full = econ_platform_core.tickers.TickerFull(full_ticker)
        meta.Exists = True
        try:
            meta.series_provider_code, meta.ticker_query = econ_platform_core.utils.split_ticker_information(full_ticker)
        except:
            raise econ_platform_core.entity_and_errors.PlatformError('Invalid full ticker')
        return meta

    def Write(self, ser, series_meta, overwrite=True):
        """

        :param ser: pandas.Series
        :param series_meta: econ_platform_core.SeriesMetadata
        :param overwrite: bool
        :return:
        """
        self.CheckDirectory()
        if not overwrite:
            raise NotImplementedError()
        full_name = self.GetFileName(series_meta.ticker_full, full_path=True)
        econ_platform_core.log_debug('Writing to %s', full_name)
        ser.to_csv(path_or_buf=full_name, sep='\t', header=True)

    def GetAllValidSeriesTickers(self):
        """
        Returns a list of all the valid full tickers in the database.

        Used for database tansfers
        :return: list
        """
        self.CheckDirectory()
        flist = os.listdir(self.Directory)
        out = []
        for fname in flist:
            try:
                meta = self.GetMetaFromFile(os.path.join(self.Directory, fname))
                out.append(meta.ticker_full)
            except:
                pass
        return out

    def GetLastRefresh(self, ticker_full):
        """
        Get the file modification time stamp,
        :param ticker_full: TickerFull
        :return: datetime.datatime
        """
        self.CheckDirectory()
        file_name = self.GetFileName(ticker_full, full_path=True)
        t = os.path.getmtime(file_name)
        return datetime.datetime.fromtimestamp(t)

    def SetLastRefresh(self, ticker_full, time_stamp=None):
        """
        Set the last refresh date (touch the file). Does not support non-None time_stamp...
        :param ticker_full: TickerFull
        :param time_stamp: datetime.datetime
        :return: None
        """
        self.CheckDirectory()
        file_name = self.GetFileName(ticker_full, full_path=True)
        if time_stamp is not None:
            raise NotImplementedError('This database does not support setting the refresh date to arbitrary times.')
        pathlib.Path(file_name).touch(exist_ok=True)

    def SetLastUpdate(self, ticker_full, time_stamp=None):
        """
        This method should not be called, since this class has SetsLastUpdateAutomatically=True.
        Does the same thing as SetLastRefresh() [which it just calls]

        :param ticker_full: TickerFull
        :param time_stamp: datetime.datetime
        :return:
        """
        self.SetLastRefresh(ticker_full, time_stamp)

