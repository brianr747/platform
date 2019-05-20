"""
canadian_recession.py

Creates a time series of Canadian Recession dates as a user series.

Taken from C.D. Howe Business Cycle Council: https://www.cdhowe.org/council/business-cycle-council

Dates from file (Format looks like it will be unstable...

Business Cycle Council (2017)

April 1929 (1929:Q2) 	February 1933 (1933:Q1)
November 1937 (1937:Q3) 	June 1938 (1938:Q2)
August 1947 (1947:Q2) 	March 1948 (1948:Q1)
April 1951 (1951:Q1) 	December 1951 (1951:Q4)
July 1953 (1953:Q2) 	July 1954 (1954:Q2)
March 1957(1957:Q1) 	January 1958 (1958:Q1)
March 1960 (1960:Q1) 	March 1961 (1961:Q1)
October 1974 (1974:Q3) 	March 1975 (1975:Q1)
June 1981 (1981:Q2) 	October 1982 (1982:Q4)
March 1990 (1990:Q1) 	April 1992 (1992:Q2)
October 2008 (2008:Q3) 	May 2009 (2009:Q2)

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
import dateutil
import datetime
import econ_platform_core
import econ_platform_core.providers.provider_user

# tab-delimited
data = """
April 1929\t February 1933
November 1937\t June 1938
August 1947\t March 1948
April 1951\t December 1951
July 1953\t July 1954
March 1957\t January 1958
March 1960\t March 1961
October 1974\t March 1975
June 1981\t October 1982
March 1990\t April 1992
October 2008\tMay 2009"""

extension_name = 'Canadian Recessions User Series'

def fetch_recession(series_meta):
    """

    :param series_meta: econ_platform_core.SeriesMetadata
    :return: pandas.Series
    """
    parsed_dates = data.split('\n')
    recession_pairs = []
    for row in parsed_dates:
        row = row.split('\t')
        if not len(row) == 2:
            continue
        recession_pairs.append([pandas.to_datetime(dateutil.parser.parse('1 ' + x).date()) for x in row])
    # MS = Month start frequency.
    date_axis = pandas.date_range(start=datetime.date(1929, 1, 1), end=datetime.date.today(), freq='MS')
    values = [0.] * len(date_axis)
    ser = pandas.Series(values)
    ser.index = date_axis
    ser.name = str(series_meta.ticker_full)
    for start, end in recession_pairs:
        ser[start:end] = 1.
    series_meta.series_name = 'Canadian Recession Series (C.D. Howe)'
    series_meta.series_description = 'Canadian recession dates from C.D. Howe Business Cycle Council. Manually updated.'
    series_meta.series_web_page = 'https://www.cdhowe.org/council/business-cycle-council'
    return ser, series_meta




def main():
    """
    Insert the Canadian recession indicator generator.
    :return:
    """
    econ_platform_core.Providers.UserProvider.SeriesMapper['CANADIAN_RECESSIONS'] = fetch_recession


if __name__ == '__main__':
    main()