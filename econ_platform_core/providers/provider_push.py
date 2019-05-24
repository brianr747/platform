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


class ProviderPushOnly(econ_platform_core.ProviderWrapper):
    def __init__(self):
        super(ProviderPushOnly, self).__init__(name='PushOnly')
        self.PushOnly = True

    def fetch(self, series_meta):
        """
        Get a series
        :param series_meta: econ_platform_core.SeriesMetadata
        :return: pandas.Series
        """
        raise econ_platform_core.PlatformError('The data from this provider is only pushed.')

    def PushSeries(self, ser, series_meta, database, overwrite=True):
        """
        Utility function to be called for pushing data.
        :param ser: pandas.Series
        :param series_meta: econ_platform_core.SeriesMetadata
        :param database: str
        :return:
        """
        econ_platform_core.Databases[database].Write(ser, series_meta, overwrite)