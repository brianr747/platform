"""
provider_JST_macrohistory.py

JORDÀ-SCHULARICK-TAYLOR MACROHISTORY DATABASE

Note: these data are in an Excel spreadsheet (XLSX); the user needs to download and place it in the appropriate
directory (based on config settings). The code assumes that there is only one spreadsheet in the directory.

Description from the website: http://www.macrohistory.net/data/

The Jordà-Schularick-Taylor Macrohistory Database is the result of an extensive data collection effort over several
years. In one place it brings together macroeconomic data that previously had been dispersed across a variety of
sources. On this website, we provide convenient no-cost open access under a license to the most extensive long-run
macro-financial dataset to date. Under the Terms of Use and Licence Terms below, the data is made freely available,
expressly forbidding commercial data providers from integrating, in addition to any existing data they may already
provide, all or parts of the dataset into their services, or to sell the data.

The database covers 17 advanced economies since 1870 on an annual basis. It comprises 45 real and nominal variables.
Among these, there are time series that had been hitherto unavailable to researchers, among them financial variables
such as bank credit to the non-financial private sector, mortgage lending and long-term returns on housing, equities,
bonds and bills. The database captures the near-universe of advanced-country macroeconomic and asset price dynamics,
covering on average over 90 percent of advanced-economy output and over 50 percent of world output.

Assembling the database, we relied on the input from colleagues, coauthors and doctoral students in many countries,
and consulted a broad range of historical sources and various publications of statistical offices and central banks.
For some countries we extended existing data series, for others, we relied on recent data collection efforts by others.
Yet in a non-negligible number of cases, we had to go back to archival sources including documents from governments,
central banks, and private banks. Typically, we combined information from various sources and spliced series to create
long-run datasets spanning the entire 1870–2016 period for the first time. The table below lists the available series.

---------------------------- CITATION OF DATA ------------------------------------------------------------------------
[From provider website.]

There are two citations to consider, depending on the data used. Please read this section to the end.

Under the terms of use, any information taken directly or indirectly from this source should be cited as Òscar Jordà,
Moritz Schularick, and Alan M. Taylor. 2017. “Macrofinancial History and the New Business Cycle Facts.” in NBER
Macroeconomics Annual 2016, volume 31, edited by Martin Eichenbaum and Jonathan A. Parker. Chicago: University of
Chicago Press.

However, those using any data pertaining to rates of return should cite Òscar Jordà, Katharina Knoll, Dmitry Kuvshinov,
Moritz Schularick, and Alan M. Taylor. 2019. “The Rate of Return on Everything, 1870–2015.” Quarterly Journal of
Economics. Forthcoming

We advise making explicit reference to the date when the database was consulted, as statistics are subject to revisions.

--------------- END CITATION NOTE ------------------------------------------------------------------------------------

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
import datetime

import econ_platform_core
from econ_platform_core import log, log_warning, log_debug
import econ_platform_core.configuration
import econ_platform_core.tickers as tickers
import econ_platform_core.utils


class ProviderJSTMacrohistory(econ_platform_core.ProviderWrapper):
    """
    Jordà-Schularick-Taylor Macrohistory Database XLS parser.

    This spreadsheet was so different from the Australian data that it did not make sense to try to
    find into the XLS fetcher class.
    """
    def __init__(self):
        super().__init__(name='JST_Macrohistory')
        self.WebPage = 'http://www.macrohistory.net/data/#DownloadData'
        self.Directory = None


    def fetch(self, series_meta):
        if self.Directory is None:
            self.Directory = econ_platform_core.utils.parse_config_path(
                econ_platform_core.PlatformConfiguration['P_JST']['directory'])
        flist = glob.glob(os.path.join(self.Directory, '*.xlsx'))
        # Excel can lock files, throw them out...
        flist = [x for x in flist if not '~' in x]
        if len(flist) == 0:
            raise econ_platform_core.PlatformError('No XLSX file in {0}'.format(self.Directory))
        if len(flist) > 1:
            raise econ_platform_core.PlatformError('More than one XLSX file in {0}: cannot tell which to use'.format(
                self.Directory))
        fname = flist[0]
        log_debug('Reading %s', fname)
        data_sheet = pandas.read_excel(fname, sheet_name='Data', header=0)
        description_sheet = pandas.read_excel(fname, sheet_name='Variable description', index_col=0, header=None)
        # All data is in one giant honkin' DataFrame, with one row per country per year.
        # To generate time series, need to select one country at a time.
        country_list = set(data_sheet['country'])
        self.TableWasFetched = True
        self.TableMeta = {}
        self.TableSeries = {}
        for country in country_list:
            df = data_sheet.loc[data_sheet['country'] == country]
            iso_code = df['iso'][df.index[0]]
            # Now, blast through the data types.
            dates = df['year']
            cal_dates = [datetime.date(x, 1, 1) for x in dates]
            exclusions = ('year', 'iso', 'country', 'ifs')
            for c in df.columns:
                if c in exclusions:
                    continue
                ser = pandas.Series(df[c])
                ser.index = cal_dates
                meta = econ_platform_core.SeriesMetadata()
                meta.series_provider_code = econ_platform_core.tickers.TickerProviderCode(self.ProviderCode)
                meta.ticker_query = econ_platform_core.tickers.TickerFetch('{0} {1}'.format(iso_code, c))
                meta.ticker_full = econ_platform_core.tickers.create_ticker_full(meta.series_provider_code,
                                                                                 meta.ticker_query)
                meta.series_name = '{0} {1}'.format(country, description_sheet.at[c,1])
                meta.series_description = '{0} from Jordà-Schularick-Taylor Macrohistory Database'.format(
                    meta.series_name)
                full_str = str(meta.ticker_full)
                self.TableSeries[full_str] = ser
                self.TableMeta[full_str] = meta
        try:
            ser = self.TableSeries[str(series_meta.ticker_full)]
            meta = self.TableMeta[str(series_meta.ticker_full)]
            return ser, meta
        except KeyError:
            raise econ_platform_core.TickerNotFoundError('{0} not found'.format(str(series_meta.ticker_full)))



