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

import myplatform
import myplatform.utils


class DatabaseText(myplatform.DatabaseManager):
    def __init__(self):
        super().__init__('Text File Database')
        self.Directory = None

    def CheckDirectory(self):
        if self.Directory is None:
            self.Directory = myplatform.PlatformConfiguration['D_TEXT']['directory']
            if self.Directory == 'text_database':
                self.Directory = os.path.join(myplatform.utils.get_platform_directory(), 'text_database')

    @staticmethod
    def GetFileName(ticker):
        return myplatform.utils.convert_ticker_to_variable(ticker) + '.txt'

    def Exists(self, ticker):
        self.CheckDirectory()
        full_file = os.path.join(self.Directory, DatabaseText.GetFileName(ticker))
        return os.path.exists(full_file)

    def Retrieve(self, series_meta):
        try:
            ticker = series_meta.ticker_full
        except:
            ticker = series_meta
        self.CheckDirectory()
        full_name = os.path.join(self.Directory, DatabaseText.GetFileName(ticker))
        df = pandas.read_csv(filepath_or_buffer=full_name, sep='\t', parse_dates=True, index_col=0)
        ser = pandas.Series(df[df.columns[0]])
        return ser

    def GetMeta(self, full_ticker):
        self.CheckDirectory()
        full_name = os.path.join(self.Directory, DatabaseText.GetFileName(full_ticker))
        if not os.path.exists(full_name):
            raise myplatform.TickerNotFoundError('Unknown ticker: {0}'.format(full_ticker))
        return self.GetMetaFromFile(full_name)

    def GetMetaFromFile(self, full_name):
        # Just read the first line.
        f = open(full_name, 'r')
        header = f.readline()
        header = header.rstrip()
        try:
            dummy, full_ticker = header.split('\t')
        except:
            raise myplatform.PlatformError('Corrupt file: {0}'.format(full_name))
        meta = myplatform.SeriesMetaData()
        meta.ticker_full = full_ticker
        meta.Exists = True
        try:
            meta.series_provider_code, meta.ticker_query = myplatform.utils.split_ticker_information(full_ticker)
        except:
            raise myplatform.PlatformError('Invalid full ticker')
        return meta

    def Write(self, ser, series_meta, overwrite=True):
        """

        :param ser: pandas.Series
        :param series_meta: myplatform.SeriesMetaData
        :param overwrite: bool
        :return:
        """
        self.CheckDirectory()
        if not overwrite:
            raise NotImplementedError()
        ticker = series_meta.ticker_full
        full_name = os.path.join(self.Directory, DatabaseText.GetFileName(ticker))
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


