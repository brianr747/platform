"""
provider_example.py

Dummy provider used for testing

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
import pandas
import datetime


def get_test_series(str_ticker):
    """
    Pull this logic out so that test code can directly call this with just the string.
    """
    if str_ticker == 'TEST1':
        x = [1, 2, ]
        data = pandas.Series(x)
        data.index = [datetime.date(2000, 1, 1), datetime.date(2000, 1, 2)]
        data.name = 'TEST1'
        return data
    # If we get here, boum.
    raise KeyError('Unknown test series ' + str_ticker)



def add_example_provider():
    """
    Call this function to add the "TEST" provider.
    :return:
    """
    econ_platform_core.Providers.AddProvider(ProviderExample())

class ProviderExample(econ_platform_core.ProviderWrapper):
    def __init__(self):
        super(ProviderExample, self).__init__(name='Example Provider')


    def fetch(self, series_meta):
        """

        :param series_meta: econ_platform_core.SeriesMetaData
        :return: pandas.Series
        """
        query_ticker = str(series_meta.ticker_query)
        try:
            data = get_test_series(query_ticker)
            return data
        except KeyError:
            raise econ_platform_core.TickerNotFoundError('Not found on TEST: {0}'.format(query_ticker))
