"""
provider_quandl.py

Functions to fetch data from Quandl, and convert to standard format.

Quandl website: https://www.quandl.com/

You need an API key if you do more than 50 (?) queries per day.


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

import quandl


import myplatform


class ProviderQuandl(myplatform.ProviderWrapper):
    def __init__(self):
        super(ProviderQuandl, self).__init__(name='QUANDL')


    def fetch(self, query_ticker):
        """
        Do the fetch; will puke if you do too many queries in a day without an API key.


        Can only support single series queries...
        :param query_ticker: str
        :return: list
        """
        df = quandl.get(query_ticker)
        # Need to convert to series.
        ser = df["Value"]
        ser.index = df.index
        ser.name = '{0}@{1}'.format(self.ProviderCode, query_ticker)
        return [ser,]
