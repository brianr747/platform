"""
provider_abs_xls.py

Although the Australian Bureau of Statistics has an SDMX interface, I could not not find the series I was looking for.

I was able to find the series in xls files. So guess what? Need another provider (sigh).

This module assumes that you have extracted the xls files to abs_xls sub-directory, and searches through them.
Each file has an index sheet that gives you the "Series ID" that specifies the series.

This module is vulnerable to XLS format changes. However, the SDMX interface might be cleaned up before that happens,
and this module would not not be needed.

If I cared enough about Australian statistics, I would work on importing the whole spreadsheet. However, since I
only want a few series, that is overkill.

IN order to make this module somewhat user-friendly, should extract a manifest of all series in all spreadsheets,
and then the user can browse the meta-data. I think this should be done in a "support table," a platform functionality
that would also be very useful for CANSIM_CSV.

KNOWN ISSUE: The request from the provider uses a funky date format that R could not handle. However. subsequent
fetches from the database worked fine.

NOTE: Without the "xlrd" module, the pandas.read_excel() call will fail.

This dependency on xlrd (which was not installed when I did a pip install on pandas) means that this module is not
inside econ_platform_core, even though there are no visible problematic imports.

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
import glob

import econ_platform_core
from econ_platform_core import log, log_warning
import econ_platform_core.configuration
import econ_platform_core.tickers as tickers
import econ_platform_core.utils


class ProviderAbsXls(econ_platform_core.ProviderWrapper):
    def __init__(self):
        super(ProviderAbsXls, self).__init__(name='ABS_XLS')
        # Directory is not configurable for now.
        self.Directory = os.path.join(os.path.dirname(__file__), 'abs_xls')


    def fetch(self, series_meta):
        """

        :param series_meta: myplattform.SeriesMetadata
        :return:
        """
        # This will not be needed once the platform code is switched over to using the tickers module.
        full_ticker = tickers.TickerFull(series_meta.ticker_full)
        #provider_code, series_code = full_ticker.SplitTicker()
        series_code = series_meta.ticker_query
        df = self.SearchForSeriesCode(str(series_code))
        # Need to eliminate the after "Series ID"
        l_index = list(df.index)
        pos = l_index.index('Series ID')
        pos += 1
        ser = pandas.Series(df.values[pos:])
        ser.index = l_index[pos:]
        ser.name = str(full_ticker)
        return ser

    def SearchForSeriesCode(self, series_code):
        """

        :param series_code: str
        :return: pandas.DataFrame
        """
        # Now for the ugly solution...
        flist = glob.glob(os.path.join(self.Directory, '*.xls'))
        # Search until we find it; if we don't, puke
        for fname in flist:
            # This query pattern will work on the "data" sheets; ignore the index.
            try:
                sheets = pandas.read_excel(fname, sheet_name=None, header=None, index_col=0)
            except:
                econ_platform_core.log_last_error()
                log_warning('Problem with Excel {0}'.format(fname))
                continue
            for sheet_name in sheets:
                sheet = sheets[sheet_name]
                list_index = list(sheet.index)
                # We ignore sheets that do not match the desired format.
                if 'Series ID' not in list_index:
                    continue
                for c in sheet.columns:
                    if sheet[c]["Series ID"] == series_code:
                        list_index[0] = 'series_name'
                        sheet.index = list_index
                        return sheet[c]
        # Did not find it; puke.
        raise econ_platform_core.TickerNotFoundError('Could not find series ID = {0}'.format(series_code))




