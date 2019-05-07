"""
Script that transfers all series from the TEXT database to the SQLite database.

Note: the TEXT database series to have the correct ticker_full as the column header.
"""



import myplatform

myplatform.start_log()
myplatform.Databases['SQLITE'].LogSQL = True
ticker_list = myplatform.Databases['TEXT'].GetAllValidSeriesTickers()
for ticker in ticker_list:
    myplatform.Databases.TransferSeries(ticker, 'TEXT', 'SQLITE')
