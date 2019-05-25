"""

SeriesMetadata class.

Will add more conversion options over time, to make serialisation easier.

The key point to this class is that it uses the ticker classes to enforce that code puts the
correct ticker type in the slots (although it might not be able to distinguish some types of tickers). This
is aimed to prevent errors from people mixing up the five (!) "ticker" types.

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

from econ_platform_core.tickers import TickerProviderCode, TickerFull, TickerLocal, TickerDataType, TickerFetch

from econ_platform_core.entity_and_errors import PlatformError, PlatformEntity


class SeriesMetadata(PlatformEntity):
    """
    Class that holds series meta data used on the platform.

    Note that ticker members are class objects (or None), and not strings. This is done to prevent mixups among ticker
    types causing hard-to-detect problems.

    Note: class data members were lower case so that they matched my database column naming convention.
    Probably a mistake to do it that way; should have made the database CamelCase.

    Will add methods to aid pushing/pulling data from databases.

    The "frequency" member is not standardised yet.

    Manifest: Standard order of "core" data fields.
    """
    Manifest = """self.Exists
self.series_id
self.series_provider_code
self.ticker_full
self.ticker_local
self.ticker_datatype
self.ticker_query
self.series_name
self.series_description
self.frequency
self.series_web_page""".replace('self.', '').split('\n')
    def __init__(self):
        # Kind of strange, but does this series yet exist on the database in question?
        super().__init__()
        self.Exists = False
        self.series_id = None
        self.series_provider_code = None
        self.ticker_full = None
        self.ticker_local = None
        self.ticker_datatype = None
        self.ticker_query = None
        self.series_name = None
        self.series_description = None
        self.series_web_page = None
        self.frequency = None
        self.ProviderMetadata = {}

    def AssertValid(self):
        """
        Are tickers valid? Use this call defensively to force internal calls to use the Ticker objects,
        not strings.

        Tickers can either be empty strings, or else of the valid ticker type.
        :return:
        """
        things_to_test = (('series_provider_code', TickerProviderCode),
                          ('ticker_full', TickerFull),
                          ('ticker_local', TickerLocal),
                          ('ticker_datatype', TickerDataType),
                          ('ticker_query', TickerFetch))
        for attrib, targ in things_to_test:
            obj = getattr(self, attrib)
            # noinspection PyPep8Naming
            OK = (obj is None) or (type(obj) is targ)
            if not OK:
                raise PlatformError('Invalid SeriesMetadata: {0} is not {1}'.format(attrib, targ))
        return True

    def __setitem__(self, key, value):
        """
        This override will automatically map strings to the appropriate ticker types.

        That is, if you go:
        metadata['ticker_local'] = 'ZZZ'
        it will set metadata.ticker_local = TickerLocal('ZZZ')

        This is useful for database routines that would otherwise have to map each ticker type to the
        appropriate class.

        :param key: str
        :param value:
        :return:
        """
        type_mapper = {
            'series_provider_code': TickerProviderCode,
            'ticker_full': TickerFull,
            'ticker_local': TickerLocal,
            'ticker_datatype': TickerDataType,
            'ticker_query': TickerFetch}
        if key in type_mapper:
            if value is None:
                setattr(self, key, None)
            else:
                setattr(self, key, type_mapper[key](value))
        else:
            setattr(self, key, value)

    def __str__(self):
        out = ''
        for name in dir(self):
            if name.startswith('_'):
                continue
            out += '{0}\t{1}\n'.format(name, str(getattr(self, name)))
        return out

    def to_DF(self):
        """
        Return data as a DataFrame. Variable size, since provider data can vary.
        :return: pandas.DataFrame
        """
        out_index = []
        out = []
        for k in SeriesMetadata.Manifest:
            out_index.append(k)
            out.append(getattr(self, k))
        out_index.append('num_provider_data')
        if len(self.ProviderMetadata) == 0:
            self.ProviderMetadata = {'TEST_FIELD': None}
        out.append(len(self.ProviderMetadata))
        keyz = list(self.ProviderMetadata.keys())
        for k in keyz:
            out_index.append(k)
            out.append(self.ProviderMetadata[k])
        keyz.sort()
        df = pandas.DataFrame(data=out, index=out_index)
        return df