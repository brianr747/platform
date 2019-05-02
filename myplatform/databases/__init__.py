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

import pandas


class DatabaseManager(object):
    def Exists(self, ticker):
        """

        :param ticker: str
        :return: bool
        """
        raise NotImplementedError()

    def Write(self, ser, ticker):
        """

        :param ser: pandas.Series
        :param ticker: str
        :return:
        """
        raise NotImplementedError()

class DatabaseList(object):
    def __init__(self):
        self.DatabaseDict = {}

    def Initialise(self):
        import myplatform.databases.text_database
        self.DatabaseDict['TEXT'] = text_database.TextDatabase()

    def __getitem__(self, item):
        """
        Access method
        :param item: str
        :return: DatabaseManager
        """
        if len(self.DatabaseDict) == 0:
            self.Initialise()
        return self.DatabaseDict[item]


Databases = DatabaseList()