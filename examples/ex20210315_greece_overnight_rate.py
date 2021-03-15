"""
Another example of creating a user series, this time from reading a spreadsheet from the Bank of Greece.

Webpage: https://www.bankofgreece.gr/en/statistics/financial-markets-and-interest-rates/drachma-money-market-rates
File URL: https://www.bankofgreece.gr/RelatedDocuments/drachma_overnight_rate.xls

I will leave the user to download the file manually, to avoid any risks of scripts bombarding the Bank of Greece.

This single series is not really enough to justify creating a new add-in, but once I accumulate enough of them,
I will take a look at create a "miscellaneous" data source file.

"""

import pandas

from econ_platform_core import fetch, Providers
from econ_platform.start import quick_plot
import econ_platform_core.tickers as tickers

#---------------------------------------------------------------------------------------
# Normally, the user-defined series would be handled in a library. Kept here to keep
# Example self-contained.
def greek_overnight(series_meta):
    """

    :param series_meta: econ_platform_core.SeriesMetadata
    :return:
    """
    if not str(series_meta.ticker_query) in ('GREEK_DRACHMA_OVERNIGHT_AVG',
            'GREEK_DRACHMA_OVERNIGHT_EOM'):
        raise ValueError('Wrong series!')
    full_ticker = tickers.TickerFull(series_meta.ticker_full)
    # I will assume that the file is downloaded to the current directory
    sheet = pandas.read_excel('drachma_overnight_rate.xls',  header=2)
    if str(series_meta.ticker_query) == 'GREEK_DRACHMA_OVERNIGHT_AVG':
        ser = pandas.Series(sheet['monthly averages'])
        ser.index = sheet['Unnamed: 0']
        series_meta.series_name = 'Average pre-Euro Greek Drachma Bank Overnight Rate'
        series_meta.series_description = 'Monthly average bank overnight rate from Bank of Greece'
        # quick_plot(ser)
    else:
        print(sheet)
        raise NotImplementedError('Bam!')
    ser.name = str(full_ticker)
    return ser
# Push the handler into the UserProvider
user_provider = Providers.UserProvider
user_provider.SeriesMapper['GREEK_DRACHMA_OVERNIGHT_AVG'] = greek_overnight
user_provider.SeriesMapper['GREEK_DRACHMA_OVERNIGHT_EOM'] = greek_overnight
# End of code that should be in a library.
#--------------------------------------------------------------------


# Now we can fetch it.
ser = fetch('U@GREEK_DRACHMA_OVERNIGHT_AVG')
quick_plot(ser)