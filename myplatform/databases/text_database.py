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

class TextDatabase(myplatform.DatabaseManager):
    def __init__(self):
        super().__init__()
        self.Name = 'TEXT'
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
        full_file = os.path.join(self.Directory, TextDatabase.GetFileName(ticker))
        return os.path.exists(full_file)

    def Retrieve(self, ticker):
        self.CheckDirectory()
        full_name = os.path.join(self.Directory, TextDatabase.GetFileName(ticker))
        df = pandas.read_csv(filepath_or_buffer=full_name, sep='\t', parse_dates=True, index_col=0)
        ser = pandas.Series(df[df.columns[0]])
        return ser

    def Write(self, ser, ticker):
        """

        :param ser: pandas.Series
        :param ticker: str
        :return:
        """
        self.CheckDirectory()
        full_name = os.path.join(self.Directory, TextDatabase.GetFileName(ticker))
        ser.to_csv(path_or_buf=full_name, sep='\t', header=True)


