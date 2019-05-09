"""
Script that transfers all series from the TEXT database to the SQLite database.

Note: the TEXT database series to have the correct ticker_full as the column header.
"""


import econ_platform_core
import econ_platform.start

econ_platform_core.start_log()
econ_platform_core.Databases['SQLITE'].LogSQL = True
ticker_list = econ_platform_core.Databases['TEXT'].GetAllValidSeriesTickers()
for ticker in ticker_list:
    econ_platform_core.Databases.TransferSeries(ticker, 'TEXT', 'SQLITE')
