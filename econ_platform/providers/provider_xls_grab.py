"""
provider_xls_grab.py

Base class for XLS grabbing.

RBA_XLS derives from this class, and it should be a small refactoring for ABS_XLS.

Later on, could make more flexible if needed.

NOTE: Without the "xlrd" module, the pandas.read_excel() call will fail.

This dependency on xlrd (which was not installed when I did a pip install on pandas) means that this module is not
inside econ_platform_core, even though there are no visible problematic imports.
"""


import os
import pandas
import glob

import econ_platform_core
import econ_platform_core.entity_and_errors
import econ_platform_core.series_metadata
from econ_platform_core import log, log_warning, log_debug
import econ_platform_core.configuration
import econ_platform_core.tickers as tickers
import econ_platform_core.utils

class SkipColumn(Exception):
    pass

class ProviderXlsGrab(econ_platform_core.ProviderWrapper):
    def __init__(self, name='XLS_GRAB'):
        super(ProviderXlsGrab, self).__init__(name=name)
        # Look up config only when fetch is called, since configuration parsing may
        # not yet have happened.
        self.Directory = None
        self.Dialect = None
        self.TickerLabels = tuple()
        self.SeriesNameLabel = None
        self.SeriesDescriptionLabel = None

    def SetDirectory(self):
        raise NotImplementedError()


    def fetch(self, series_meta):
        """

        :param series_meta: econ_platform_core.SeriesMetadata
        :return: pandas.Series
        """
        if not self.Dialect == 'Australian':
            raise NotImplementedError('Only "Australian" XLS format supported')
        if self.Directory is None:
            self.SetDirectory()
        self.TableWasFetched = True
        self.TableMeta = {}
        self.TableSeries = {}

        full_ticker = series_meta.ticker_full
        self.BuildTable()
        try:
            ser = self.TableSeries[str(full_ticker)]
            meta = self.TableMeta[str(full_ticker)]
            return ser, meta
        except:
            raise econ_platform_core.entity_and_errors.TickerNotFoundError('{0} not found'.format(str(full_ticker)))

    def FixIndex(self, df_index):
        """
        Override this method to fix teh dataframe index. Needed for ABS_XLS
        :param df_index:
        :return:
        """
        return df_index

    def BuildTable(self):
        """
        Get all series in all xls in directory (!).
        """
        # Now for the ugly solution...
        flist = glob.glob(os.path.join(self.Directory, '*.xls'))
        # Search until we find it; if we don't, puke
        out = []
        for fname in flist:
            log_debug('Reading %s', fname)
            # This query pattern will work on the "data" sheets; ignore the index.
            try:
                sheets = pandas.read_excel(fname, sheet_name=None, header=None, index_col=0)
            except:
                econ_platform_core.log_last_error()
                log_warning('Problem with Excel {0}'.format(fname))
                continue
            for sheet_name in sheets:
                sheet = sheets[sheet_name]
                sheet = self.PatchSheet(sheet)
                list_index = list(sheet.index)
                # We ignore sheets that do not match the desired format.
                for targ_field in self.TickerLabels:
                    if targ_field not in list_index:
                        continue
                    list_index = self.FixIndex(list_index)
                    sheet.index = list_index
                    for c in sheet.columns:
                        try:
                            [ser, meta] = self.ConvertDFtoSeries(sheet[c])
                        except SkipColumn:
                            continue
                        full_ticker = str(meta.ticker_full)
                        if full_ticker in self.TableSeries:
                            ser = ser.combine_first(self.TableSeries[full_ticker])
                            self.TableSeries[full_ticker] = ser
                        else:
                            self.TableSeries[full_ticker] = ser
                            self.TableMeta[full_ticker] = meta


    def ConvertDFtoSeries(self, df):
        l_index = list(df.index)
        pos = -1
        series_code = ''
        for targ in self.TickerLabels:
            if pos == -1:
                try:
                    pos = l_index.index(targ)
                    series_code = df[targ]
                except:
                    pos = -1
        if pos == -1:
            # Should never get here.
            raise SkipColumn()
        pos += 1
        full_ticker = tickers.create_ticker_full(self.ProviderCode, series_code)
        if 'nan' in str(full_ticker):
            raise SkipColumn()
        meta = econ_platform_core.series_metadata.SeriesMetadata()
        meta.ticker_full = full_ticker
        meta.series_provider_code = tickers.TickerProviderCode(self.ProviderCode)
        meta.ticker_query = tickers.TickerFetch(series_code)
        if self.SeriesNameLabel is not None:
            try:
                meta.series_name = df[self.SeriesNameLabel]
            except KeyError:
                pass
        if self.SeriesDescriptionLabel is not None:
            try:
                meta.series_description = df[self.SeriesDescriptionLabel]
                # Multi-line labels...
                meta.series_description = meta.series_description.replace('\n', ' ')
            except KeyError:
                pass
        if (meta.series_description is None) or (meta.series_name is None):
            self.PatchDescription(df, meta)
        ser = pandas.Series(df.values[pos:])
        ser.index = l_index[pos:]
        ser.name = str(full_ticker)
        return ser, meta

    def PatchDescription(self, df, meta):
        """
        Override this to patch the description information.
        :param df:
        :param meta:
        :return:
        """
        pass

    def PatchSheet(self, sheet):
        return sheet

