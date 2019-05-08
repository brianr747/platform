"""
provider_fred.py

Functions to fetch data from FRED (St. Louis Fed), and convert to standard format.

Challenge: You need an API key; need to contact St. Louis Fed.


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

import fredapi


import econ_platform_core


class ProviderFred(econ_platform_core.ProviderWrapper):
    def __init__(self):
        super(ProviderFred, self).__init__(name='FRED')


    def fetch(self, series_meta):
        """
        Do the fetch; will puke if do not have an API key in the config
        TODO: Look to see if FRED_API_KEY environment variable is set...

        Can only support single series queries...
        :param series_meta: str
        :return: list
        """
        query_ticker = series_meta.ticker_query
        api_key = econ_platform_core.PlatformConfiguration['P_FRED']['api_key']
        if api_key.lower() == 'none':
            # KeyError - ha, ha, I kill myself...
            raise KeyError('Error: need to set the FRED API key in the config.txt; available from St. Louis Fed.')
        fred = fredapi.Fred(api_key=api_key)
        data = fred.get_series(query_ticker)
        data.name = series_meta.ticker_full
        return [data,]
