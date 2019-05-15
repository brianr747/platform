"""
provider_rba_xls.py

Reserve Bank of Australia data. Very similar provider structure to ABS_XLS

Note that interest rate data 2013- is on DB.nomics. Unless they get the backhistory on their
platform, at the minimum, use this provider to get back data, and refresh from DB.nomics.

Note: Could absorb provider_abs_xls.py as a subclass, and/or create an abstract XLS reader base class.

Wait until we see this as worthwhile.

This module assumes that you have extracted the xls files to rba_xls sub-directory, and searches through them.
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
"""


import os
import pandas
import glob

import econ_platform_core
from econ_platform_core import log, log_warning, log_debug
import econ_platform_core.configuration
import econ_platform_core.tickers as tickers
import econ_platform_core.utils
import econ_platform.providers.provider_xls_grab


class ProviderRbaXls(econ_platform.providers.provider_xls_grab.ProviderXlsGrab):
    def __init__(self):
        super(ProviderRbaXls, self).__init__(name='RBA_XLS')
        # Look up config only when fetch is called, since configuration parsing may
        # not yet have happened.
        self.Directory = None
        self.Dialect = 'Australian'
        self.TickerLabels = ('Mnemonic', 'Series ID')
        self.SeriesNameLabel = 'Title'
        self.SeriesDescriptionLabel = 'Description'
        self.WebPage = 'https://www.rba.gov.au/statistics/tables/'

    def SetDirectory(self):
        self.Directory = econ_platform_core.utils.parse_config_path(
            econ_platform_core.PlatformConfiguration['P_RBAXLS']['directory'])

    def PatchDescription(self, df, meta):
        """
        Patch description data for historical spreadsheets: F2, F16.

        Only limited error checking, since the spreadsheet formats should not change.

        :param df:
        :param meta:
        :return:
        """
        if 'F2 ' in df.index[0]:
            issuer = df[3]
            mat = df[4]
            if ('Australian' in issuer) or ('NSW' in issuer):
                msg = '{0} {1}'.format(issuer, mat)
                meta.series_name = msg
                meta.series_description = msg
        if 'F16 INDICATIVE' in df.index[0]:
            try:
                issue_id = df["Issue ID"]
                coupon = df['Coupon']
                mat = df['Maturity']
                if not type(coupon) == str:
                    coupon = '%g%%' % ((100.*coupon),)
                if not type(mat) == str:
                    mat = mat.isoformat()[0:10]
            except:
                return
            meta.series_name = 'Yield on {0} of {1}'.format(coupon, mat)
            meta.series_description = 'Indicative Mid-Yield on {0} of {1} (Issue ID={2})'.format(
                coupon, mat, issue_id)

    def PatchSheet(self, sheet):
        """
        Patch historical data sheet for "F2  CAPITAL MARKET YIELDS - GOVERNMENT BONDS"
        :param sheet:
        :return:
        """
        if sheet.index[0] == 'F2  CAPITAL MARKET YIELDS - GOVERNMENT BONDS':
            # Only correct if missing the meta data labels. (In the historical spreadsheets.)
            if 'Description' in sheet.index:
                return sheet
            # The issuer only appears in the first column of a group. Repeat it.
            prev = ''
            for c in sheet.columns:
                if not type(sheet[c][3]) == str:
                    sheet[c][3] = prev
                else:
                    prev = sheet[c][3]
        return sheet


    # def fetch(self, series_meta):
    #     """
    #
    #     :param series_meta: myplattform.SeriesMetaData
    #     :return: pandas.Series
    #     """
    #     if self.Directory is None:
    #         self.Directory = econ_platform_core.utils.parse_config_path(
    #             econ_platform_core.PlatformConfiguration['P_RBAXLS']['directory'])
    #     # This will not be needed once the platform code is switched over to using the tickers module.
    #     full_ticker = tickers.TickerFull(series_meta.ticker_full)
    #     series_code = series_meta.ticker_query
    #     df_list = self.SearchForSeriesCode(str(series_code))
    #     ser = None
    #     for df in df_list:
    #         partial_ser = self.ConvertDFtoSeries(df, full_ticker)
    #         if ser is None:
    #             ser = partial_ser
    #         else:
    #             ser = ser.combine_first(partial_ser)
    #     return ser
    #
    # def SearchForSeriesCode(self, series_code):
    #     """
    #
    #     :param series_code: str
    #     :return: pandas.DataFrame
    #     """
    #     # Now for the ugly solution...
    #     flist = glob.glob(os.path.join(self.Directory, '*.xls'))
    #     # Search until we find it; if we don't, puke
    #     out = []
    #     for fname in flist:
    #         log_debug('Reading %s', fname)
    #         # This query pattern will work on the "data" sheets; ignore the index.
    #         try:
    #             sheets = pandas.read_excel(fname, sheet_name=None, header=None, index_col=0)
    #         except:
    #             econ_platform_core.log_last_error()
    #             log_warning('Problem with Excel {0}'.format(fname))
    #             continue
    #         for sheet_name in sheets:
    #             sheet = sheets[sheet_name]
    #             list_index = list(sheet.index)
    #             # We ignore sheets that do not match the desired format.
    #             for targ_field in self.TickerLabels:
    #                 if targ_field not in list_index:
    #                     continue
    #                 for c in sheet.columns:
    #                     if sheet[c][targ_field] == series_code:
    #                         # Fixes ABS spreadsheet
    #                         list_index[0] = 'series_name'
    #                         sheet.index = list_index
    #                         out.append(sheet[c])
    #     # Did not find it; puke.
    #     if len(out) == 0:
    #         raise econ_platform_core.TickerNotFoundError('Could not find series ID = {0}'.format(series_code))
    #     else:
    #         return out
    #
    # def ConvertDFtoSeries(self, df, full_ticker):
    #     """
    #
    #     :param df:
    #     :param full_ticker:
    #     :return:
    #     """
    #     l_index = list(df.index)
    #     pos = -1
    #     for targ in self.TickerLabels:
    #         if pos == -1:
    #             try:
    #                 pos = l_index.index(targ)
    #             except:
    #                 pos = -1
    #     if pos == -1:
    #         # Should never get here.
    #         raise ValueError('Internal logic error; cannot find data row')
    #     pos += 1
    #     ser = pandas.Series(df.values[pos:])
    #     ser.index = l_index[pos:]
    #     ser.name = str(full_ticker)
    #     return ser
    #
    #

