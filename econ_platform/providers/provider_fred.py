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
import econ_platform_core.entity_and_errors


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
        data = fred.get_series(str(query_ticker))
        data.name = str(series_meta.ticker_full)
        if not series_meta.Exists:
            return data, self.GetMeta(series_meta)
        return data

    def GetMeta(self, meta_in):
        """
        Get the metadata.
        :param metadata: econ_platform_core.SeriesMetadata
        :return: econ_platform_core.SeriesMetadata
        """
        query_ticker = meta_in.ticker_query
        api_key = econ_platform_core.PlatformConfiguration['P_FRED']['api_key']
        if api_key.lower() == 'none':
            # KeyError - ha, ha, I kill myself...
            raise KeyError('Error: need to set the FRED API key in the config.txt; available from St. Louis Fed.')
        fred = fredapi.Fred(api_key=api_key)
        data = fred.get_series_info(str(query_ticker))
        keys = data.index.to_list()
        for k in keys:
            meta_in.ProviderMetadata[k] = str(data[k])
            if k == 'frequency_short':
                meta_in.frequency = meta_in.ProviderMetadata[k]
            if k == 'title':
                meta_in.series_name = meta_in.ProviderMetadata[k]
                meta_in.series_description = '{0} From FRED {1}'.format(meta_in.ProviderMetadata[k],
                                                                        str(query_ticker))
        return meta_in

    def _GetSeriesUrlImplementation(self, series_meta):
        """
        Gets the series-specific URL. (Does not validate existence or validity of string...)
        :param series_meta:
        :return:
        """
        if series_meta.ticker_query is None:
            raise econ_platform_core.entity_and_errors.PlatformError('Need to see the query ticker in order to fetch the metadata')
        return 'https://fred.stlouisfed.org/series/{0}'.format(str(series_meta.ticker_query))


